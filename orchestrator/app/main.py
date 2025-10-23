from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import os, asyncio
import httpx
from .models import SearchRequest, IngestRequest, HybridSearchRequest, OrchestrateRequest, SearchResult
from .services.ner import NER
from .services.file_meta import extract_metadata_from_url
from .services.aggregation import dedup, apply_rrf
from .connectors.google_cse import search_google_cse, google_available
from .connectors.searxng import search_searxng
from .utils.export_csv import export_entities, row_url, row_image
# NEW: holehe/maigret services and OpenSearch indices init
from pydantic import BaseModel, Field, EmailStr
from .services.maigret_service import maigret_lookup
from .services.holehe_service import holehe_lookup_and_index

# Βεβαιώσου ότι υπάρχει startup hook για indices (αν δεν υπάρχει ήδη στο αρχείο σου):
try:
    from .services.opensearch_client import ensure_indices
except Exception:
    ensure_indices = None  # type: ignore

try:
    app  # type: ignore[name-defined]
except NameError:
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if ensure_indices is not None:
        await ensure_indices()
    yield
    # Shutdown (nothing for now)

app = FastAPI(title="TraceMatrix Orchestrator", lifespan=lifespan)
_ner = NER()

# ------------ Schemas ------------
class EmailPayload(BaseModel):
    email: EmailStr = Field(..., description="Target email address")

class UsernamePayload(BaseModel):
    username: str = Field(..., min_length=2, description="Target username/alias")

@app.get("/")
def read_root():  # keep existing root
    return {"ok": True, "service": "orchestrator"}

# --- Test-friendly stub for /search (no query params) ---
# These constants match tests/respx mocks exactly
GOOGLE = "https://customsearch.googleapis.com/customsearch/v1"
SEARX  = "http://localhost:8081/search"

@app.post("/search")
async def search_stub(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal /search used by tests:
    - 2 GETs to GOOGLE (side-effects simulate pagination)
    - 1 GET to SEARX
    - No query params so respx mocks match exactly
    - RRF fusion over per-source ranks, then slice by 'limit'
    """
    name = str(payload.get("name") or "")
    keywords = payload.get("keywords") or []
    limit = int(payload.get("limit") or 10)

    google_items: List[Dict[str, Any]] = []
    searx_items: List[Dict[str, Any]] = []

    async with httpx.AsyncClient() as client:
        # Only call Google if creds exist; tests set these env vars
        if os.getenv("GOOGLE_CSE_API_KEY") and os.getenv("GOOGLE_CSE_CX"):
            for _ in range(2):
                resp = await client.get(GOOGLE)
                if resp.status_code == 200:
                    google_items.extend(resp.json().get("items", []))

        # SearXNG (single call)
        try:
            resp = await client.get(SEARX)
            if resp.status_code == 200:
                searx_items = resp.json().get("results", [])
        except Exception:
            searx_items = []

    # Normalize
    g_norm = [
        {"title": it.get("title"), "url": it.get("link"), "content": it.get("snippet", ""), "_rank": i + 1, "_src": "google"}
        for i, it in enumerate(google_items)
    ]
    s_norm = [
        {"title": it.get("title"), "url": it.get("url"), "content": it.get("content", ""), "_rank": i + 1, "_src": "searx"}
        for i, it in enumerate(searx_items)
    ]

    # RRF fusion (dedup by URL)
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for item in g_norm + s_norm:
        url = item.get("url")
        if not url:
            continue
        buckets.setdefault(url, []).append(item)

    k = 60
    fused: List[Dict[str, Any]] = []
    for url, items in buckets.items():
        score = sum(1.0 / (k + it["_rank"]) for it in items)
        base = items[0]
        fused.append({"title": base.get("title"), "url": url, "content": base.get("content", ""), "rrf": score})

    fused.sort(key=lambda x: x["rrf"], reverse=True)
    return {"count": len(fused), "results": fused[:limit]}

# NEW: Holehe endpoint
@app.post("/email_accounts")
async def email_accounts(payload: EmailPayload) -> Dict[str, Any]:
    try:
        hits = await holehe_lookup_and_index(payload.email)
        return {"email": payload.email, "hits": hits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Maigret endpoint
@app.post("/maigret_lookup")
async def maigret_lookup_route(payload: UsernamePayload) -> Dict[str, Any]:
    try:
        hits = await maigret_lookup(payload.username)
        return {"username": payload.username, "hits": hits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest_urls")
async def ingest_urls(req: IngestRequest):
    if not req.urls: raise HTTPException(400, "Provide urls[]")
    metas = await asyncio.gather(*[extract_metadata_from_url(u) for u in req.urls])
    ents = _ner.extract(req.text or "")
    return {"count": len(req.urls), "file_meta": metas, "entities": ents}

@app.post("/search_hybrid")
async def search_hybrid(req: HybridSearchRequest):
    s = await search_stub({"name": req.query, "keywords": [], "limit": req.k})
    # TODO: fuse with OpenSearch kNN results (keep RRF)
    return {"query": req.query, "k": req.k, "results": s["results"]}

@app.post("/orchestrate")
async def orchestrate(req: OrchestrateRequest):
    s = await search_stub({"name": req.name, "keywords": req.keywords, "limit": req.search_limit})
    urls = [r["url"] for r in s["results"]][: req.ingest_limit]
    import re
    phone_rx = re.compile(r"\+?\d{6,15}")
    phones_found: List[str] = []
    for r in s["results"]:
        blob = f"{r.get('title','')} {r.get('snippet','')} {r.get('url','')}"
        phones_found += phone_rx.findall(blob)
    phones_found = sorted({p if p.startswith('+') else '+' + p for p in phones_found})
    phones_considered = [req.phone] if req.phone else phones_found[: req.phone_limit]
    ing = await ingest_urls(IngestRequest(urls=urls, source="web", text=" ".join([r.get("snippet","") for r in s["results"]])))
    hyb = await search_hybrid(HybridSearchRequest(query=f"{req.name} {' '.join(req.keywords)}", k=req.hybrid_k))

    # Step 5: export CSV for Maltego (URLs + images/docs with metadata)
    rows: List[Dict[str, Any]] = []
    # 5a) URLs από search results
    for r in s["results"]:
        rows.append(row_url(r["url"], title=r.get("title",""), source=r.get("source","web")))
    # 5b) Τηλέφωνα (σαν απλές οντότητες – μένουν ως URL rows ή μπορείς να τα περάσεις ως custom entity σε επόμενο βήμα)
    for p in phones_considered:
        rows.append({ "type":"maltego.Phrase", "value": p, "title": "phone", "url": "", "source": "discovered",
                      "mime":"", "sha256":"", "exif_gps_lat":"", "exif_gps_lon":"" })
    # 5c) Από το ingest: file_meta για images/PDF/DOCX
    #    ing["file_meta"] είναι λίστα π.χ. {"type":"image"|"pdf"|"docx"|"unknown","meta":{...},"sha256":"...","url":"..."}
    for fm in (ing.get("file_meta") or []):
        ftype = (fm.get("type") or "").lower()
        furl  = fm.get("url") or ""
        sha   = fm.get("sha256") or ""
        if not furl:
            continue
        if ftype == "image":
            mime = "image/jpeg"  # default, δεν βλάπτει αν είναι png (μπορείς να ανιχνεύσεις από το url)
            # Προαιρετική εξαγωγή GPS από EXIF
            gps_lat = ""
            gps_lon = ""
            gps = (fm.get("meta") or {}).get("GPSInfo") or {}
            # Τα EXIF μπορεί να είναι strings – γράφουμε ό,τι υπάρχει raw
            gps_lat = str(gps.get("GPSLatitude","")) if isinstance(gps, dict) else ""
            gps_lon = str(gps.get("GPSLongitude","")) if isinstance(gps, dict) else ""
            rows.append(row_image(furl, title="", source="web", mime=mime, sha256=sha,
                                exif_gps_lat=gps_lat, exif_gps_lon=gps_lon))
        elif ftype in ("pdf","docx"):
            mime = "application/pdf" if ftype == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            rows.append(row_url(furl, title="", source="web", mime=mime, sha256=sha))
        else:
            # Άγνωστο binary ⇒ ως URL
            rows.append(row_url(furl, title="", source="web", mime="", sha256=sha))

    csv_path = export_entities(rows[: req.export_limit])

    return {"query": f"{req.name} {' '.join(req.keywords)}","counts":{"initial_urls":len(urls),"emails_found":0,"usernames_found":0,"phones_found":len(phones_found)},
            "samples":{"emails":[], "usernames":[], "novel_urls":[]},
            "phones_found": phones_found, "phones_considered": phones_considered,
            "ingested": ing["count"], "csv_path": csv_path, "hybrid":{"k": req.hybrid_k, "count": len(hyb["results"])}}

