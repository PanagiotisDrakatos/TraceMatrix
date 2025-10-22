from __future__ import annotations
import os
from typing import Dict, Any, List
from opensearchpy import OpenSearch, RequestsHttpConnection

OS_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
INDEX = os.getenv("OSINT_INDEX", "osint_pages")
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))


def client() -> OpenSearch:
    return OpenSearch(
        hosts=[OS_URL],
        use_ssl=OS_URL.startswith("https://"),
        verify_certs=False,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )


def create_index_if_not_exists():
    c = client()
    if c.indices.exists(index=INDEX):
        return True
    body = {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                "url": {"type": "keyword"},
                "title": {"type": "text"},
                "snippet": {"type": "text"},
                "content": {"type": "text"},
                "source": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "vector": {"type": "knn_vector", "dimension": EMBED_DIM},
            }
        },
    }
    try:
        c.indices.create(index=INDEX, body=body)
    except Exception:
        # ignore if already exists due to race
        pass
    return True


def index_doc(doc: Dict[str, Any]):
    client().index(index=INDEX, body=doc, id=doc.get("url"))


def bm25_search(query: str, size: int = 10) -> List[Dict[str, Any]]:
    if query == "*":
        q = {"match_all": {}}
    else:
        q = {"multi_match": {"query": query, "fields": ["title^2", "snippet^1.5", "content"]}}
    res = client().search(index=INDEX, body={"size": size, "query": q})
    hits = res.get("hits", {}).get("hits", [])
    return [{"url": h["_id"], **h.get("_source", {}), "_score": h.get("_score", 0)} for h in hits]


def knn_search(vec: List[float], size: int = 10) -> List[Dict[str, Any]]:
    res = client().search(index=INDEX, body={
        "size": size,
        "query": {
            "knn": {
                "field": "vector",
                "query_vector": vec,
                "k": size,
                "num_candidates": max(size * 5, 50)
            }
        }
    })
    hits = res.get("hits", {}).get("hits", [])
    return [{"url": h["_id"], **h.get("_source", {}), "_score": h.get("_score", 0)} for h in hits]
