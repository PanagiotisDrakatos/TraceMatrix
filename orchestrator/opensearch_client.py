
from __future__ import annotations
import os
from typing import Dict, Any, Optional, List
from opensearchpy import OpenSearch, RequestsHttpConnection

OS_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
INDEX = os.getenv("OSINT_INDEX", "osint_pages")
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))

def client() -> OpenSearch:
    return OpenSearch(
        hosts=[OS_URL],
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )

def create_index_if_not_exists():
    c = client()
    if c.indices.exists(INDEX): return True
    body = {
        "settings": {"index": {"knn": True}},
        "mappings": {"properties": {
            "url": {"type": "keyword"},
            "title": {"type": "text"},
            "snippet": {"type": "text"},
            "content": {"type": "text"},
            "source": {"type": "keyword"},
            "timestamp": {"type": "date"},
            "vector": {"type": "knn_vector", "dimension": EMBED_DIM}
        }}
    }
    c.indices.create(INDEX, body=body); return True

def index_doc(doc: Dict[str, Any]):
    client().index(index=INDEX, body=doc, id=doc.get("url"))

def bm25_search(query: str, size: int = 10) -> List[Dict[str, Any]]:
    res = client().search(index=INDEX, body={
        "size": size,
        "query": {"multi_match": {"query": query, "fields": ["title^2", "snippet^1.5", "content"]}}
    })
    hits = res.get("hits", {}).get("hits", [])
    return [{"url": h["_id"], **h["_source"], "_score": h["_score"]} for h in hits]

def knn_search(vec: List[float], size: int = 10) -> List[Dict[str, Any]]:
    res = client().search(index=INDEX, body={
        "size": size,
        "query": {"knn": {"vector": {"vector": vec, "k": size}}}
    })
    hits = res.get("hits", {}).get("hits", [])
    return [{"url": h["_id"], **h["_source"], "_score": h["_score"]} for h in hits]
