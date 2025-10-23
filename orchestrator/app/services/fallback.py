from __future__ import annotations
from typing import Dict, List, Any, Tuple
import hashlib
import httpx
from .config import filename_from_template
from .exporter import export
from .media_discovery import discover_media


def _hash_title(title: str) -> str:
    return hashlib.sha1((title or "").strip().lower().encode("utf-8")).hexdigest()


async def run_hybrid(cfg: Dict[str, Any], payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    name = payload.get("name", "")
    keywords = payload.get("keywords", [])
    query = f"{name} " + " ".join(keywords)
    results: List[Dict[str, Any]] = []

    timeout = cfg.get("guardrails", {}).get("timeouts", {}).get("per_step_s", 20)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Prefer internal /search_hybrid if exists
        try:
            k = (
                cfg.get("plan", {})
                .get("steps", [{}])
                [2]
                .get("engines", {})
                .get("opensearch", {})
                .get("k", 20)
            )
            r = await client.post("http://localhost:8000/search_hybrid", json={"query": query, "k": k})
            j = r.json()
            for it in (j.get("results", []) or []):
                results.append(
                    {
                        "url": it.get("url"),
                        "title": it.get("title"),
                        "domain": it.get("domain"),
                        "source": it.get("source", "hybrid"),
                    }
                )
        except Exception:
            pass
    # Dedupe
    seen = set()
    deduped: List[Dict[str, Any]] = []
    for r in results:
        key = (r.get("url") or "") + "|" + _hash_title(r.get("title", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    return deduped


async def fallback_orchestrate(cfg: Dict[str, Any], payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    results = await run_hybrid(cfg, payload)
    media = await discover_media(cfg, payload)
    results.extend(media or [])

    exp_cfg = next((s for s in cfg.get("plan", {}).get("steps", []) if s.get("name") == "export"), None)
    if not exp_cfg:
        outdir = payload.get("export_dir") or "exports"
        fname = filename_from_template("run_{yyyy}{mm}{dd}_{HH}{MM}{SS}_{slug(name)}.ext", payload.get("name", "run"))
        csv_path, json_path = export(results, outdir, fname, payload.get("name", "run"), formats=("csv", "json"), split_by_entity=True)
        return ({"csv": csv_path, "json": json_path}, results)

    outdir = exp_cfg.get("dir") or payload.get("export_dir") or "exports"
    fname = filename_from_template(exp_cfg.get("filename_template", "run_{yyyy}{mm}{dd}_{HH}{MM}{SS}_{slug(name)}.ext"), payload.get("name", "run"))
    csv_path, json_path = export(
        results,
        outdir,
        fname,
        payload.get("name", "run"),
        formats=tuple(exp_cfg.get("formats", ["csv", "json"])),
        split_by_entity=bool(exp_cfg.get("split_by_entity", True)),
    )
    return ({"csv": csv_path, "json": json_path}, results)
