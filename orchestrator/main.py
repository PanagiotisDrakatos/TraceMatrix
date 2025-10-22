from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from hybrid_rrf import reciprocal_rank_fusion
from opensearch_client import create_index_if_not_exists, index_doc, bm25_search, knn_search
from phoneinfoga_connector import phoneinfoga_lookup
from profession_filter import matches_profession
from providers_min import google_search, verify_email_reacher
from scrape_embed import fetch_and_embed, get_model
from harvester_connector import run_theharvester

app = FastAPI(title="OSINT Orchestrator (OSS)")


class SearchRequest(BaseModel):
    name: str
    keywords: Optional[List[str]] = []
    limit: Optional[int] = 10


class VerifyEmailReq(BaseModel):
    email: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search")
def search(req: SearchRequest):
    q = f"\"{req.name}\" " + " ".join(req.keywords or [])
    try:
        google_hits = google_search(q, num=min(req.limit, 10))
    except Exception as e:
        google_hits = [{"error": "google_error", "message": str(e)}]
    ranked_urls = [it.get('url') for it in google_hits if it.get('url')]
    merged = reciprocal_rank_fusion([ranked_urls], k=req.limit)
    out = []
    for u in merged:
        snippet = next((i.get("snippet") for i in google_hits if i.get("url") == u), "")
        prof_ok = matches_profession(snippet + " " + (req.name or ""))
        out.append({"url": u, "snippet": snippet, "profession_match": prof_ok})
    return {"query": q, "results": out, "meta": {"google_count": len(google_hits)}}


@app.post("/verify_email")
def verify_email(req: VerifyEmailReq):
    res = verify_email_reacher(req.email)
    if not res:
        raise HTTPException(status_code=500, detail="Reacher call failed")
    return res


class IngestReq(BaseModel):
    urls: list[str]
    source: str | None = "web"


@app.post("/ingest_urls")
def ingest_urls(req: IngestReq):
    create_index_if_not_exists()
    results = []
    for u in req.urls:
        try:
            emb = fetch_and_embed(u)
            doc = {"url": u, "title": "", "snippet": "", "source": req.source, **emb}
            index_doc(doc)
            results.append({"url": u, "status": "ok", "chars": len(emb.get("content", ""))})
        except Exception as e:
            results.append({"url": u, "status": f"error:{e}"})
    return {"ingested": results}


class HybridReq(BaseModel):
    query: str
    k: int = 10


@app.post("/search_hybrid")
def search_hybrid(req: HybridReq):
    create_index_if_not_exists()
    bm = bm25_search(req.query, size=req.k)
    model = get_model()
    qv = model.encode([req.query])[0].tolist()
    kn = knn_search(qv, size=req.k)
    bm_urls = [d["url"] for d in bm]
    kn_urls = [d["url"] for d in kn]
    fused_urls = reciprocal_rank_fusion([bm_urls, kn_urls], k=req.k)
    url_to_doc = {d["url"]: d for d in bm + kn}
    out = [url_to_doc.get(u, {"url": u}) for u in fused_urls]
    return {"query": req.query, "results": out}


@app.get("/export_csv")
def export_csv():
    create_index_if_not_exists()
    hits = bm25_search("*", size=50)
    rows = []
    for h in hits:
        rows.append({"Person": "", "Email": "", "Phone": "", "URL": h.get("url", ""), "Title": h.get("title", ""),
                     "Snippet": h.get("snippet", ""), "Source": h.get("source", ""), "Score": h.get("_score", 0)})
    import os, pandas as pd
    out_dir = os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entities.csv")
    pd.DataFrame(rows).to_csv(out_path, index=False)
    return {"status": "ok", "file": "exports/entities.csv", "rows": len(rows)}


from social_connectors import social_analyzer_username


class SocialReq(BaseModel):
    username: str


@app.post("/social_lookup")
def social_lookup(req: SocialReq):
    return social_analyzer_username(req.username)



class HarvestReq(BaseModel):
    domain: str
    limit: int = 50
    source: str = "all"

@app.post("/harvest_email")
def harvest_email(req: HarvestReq):
    """Συλλογή emails & subdomains με theHarvester"""
    return run_theharvester(req.domain, req.limit, req.source)

class PhoneReq(BaseModel):
    number: str

@app.post("/phone_lookup")
def phone_lookup(req: PhoneReq):
    """OSINT lookup τηλεφώνου με PhoneInfoga"""
    return phoneinfoga_lookup(req.number)
