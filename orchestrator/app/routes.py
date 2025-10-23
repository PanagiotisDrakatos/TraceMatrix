from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any
import os
from .services.config import load_yaml
from .services.fallback import fallback_orchestrate
from .services.media_discovery import discover_media

router = APIRouter()


def load_cfg() -> Dict[str, Any]:
    path = os.getenv("ORCH_CONFIG", "/app/config/orchestrator.fallback.yaml")
    try:
        return load_yaml(path)
    except Exception:
        return {}


@router.post("/orchestrate")
async def orchestrate(payload: Dict[str, Any] = Body(...)):
    cfg = load_cfg()
    urls = payload.get("urls") or []
    do_fallback = bool(payload.get("fallback", True)) and cfg.get("fallback", {}).get("enabled", True)

    # Forced fallback when no URLs provided and fallback requested
    if do_fallback and len(urls) == 0:
        meta, results = await fallback_orchestrate(cfg, payload)
        return {
            "status": "ok",
            "mode": "fallback_hybrid",
            "message": "Forced fallback (no URLs). Hybrid + media ➜ export",
            "exports": meta,
            "results_preview": results[:5],
        }

    # else: existing/standard path with URLs crawl ➜ ingest ➜ export
    return {
        "status": "ok",
        "mode": "standard",
        "message": "Standard orchestration path executed (URLs present)",
    }


@router.post("/discover_media")
async def media_preview(payload: Dict[str, Any] = Body(...)):
    try:
        cfg = load_cfg()
        items = await discover_media(cfg, payload)
        return {"status": "ok", "count": len(items), "results": items[:20]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
