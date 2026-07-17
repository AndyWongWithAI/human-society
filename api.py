"""human-society API - 读 graph-data.json + articles.json，暴露 REST 接口"""
import json
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DATA_FILE = Path("/var/www/human-society.intelab.cn/graph-data.json")
ARTICLES_FILE = Path("/var/www/human-society.intelab.cn/articles.json")
app = FastAPI(title="human-society API", version="1.0", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 内存缓存：按 mtime 失效，避免每次请求全量 parse 706KB（A1: API 对外需扛得住量）
_graph_cache = {"mtime": None, "data": None}
_articles_cache = {"mtime": None, "data": None}


def load():
    if not DATA_FILE.exists():
        return {"nodes": [], "edges": [], "meta": {}}
    mtime = DATA_FILE.stat().st_mtime
    if _graph_cache["data"] is None or mtime != _graph_cache["mtime"]:
        _graph_cache["data"] = json.loads(DATA_FILE.read_text())
        _graph_cache["mtime"] = mtime
    return _graph_cache["data"]


def load_articles():
    """读 articles.json，返回完整 data（含 articles 列表 + entity_articles 映射）。失败返回空结构。"""
    if not ARTICLES_FILE.exists():
        return {"articles": [], "entity_articles": {}}
    mtime = ARTICLES_FILE.stat().st_mtime
    if _articles_cache["data"] is None or mtime != _articles_cache["mtime"]:
        _articles_cache["data"] = json.loads(ARTICLES_FILE.read_text())
        _articles_cache["mtime"] = mtime
    return _articles_cache["data"]


@app.get("/api/nodes")
def list_nodes(layer: str = None, type: str = None, status: str = None, q: str = None):
    data = load()
    nodes = data["nodes"]
    if layer:   nodes = [n for n in nodes if n["layer"] == layer]
    if type:    nodes = [n for n in nodes if n["type"] == type]
    if status:  nodes = [n for n in nodes if n.get("status") == status]
    if q:
        ql = q.lower()
        nodes = [n for n in nodes if ql in n["id"].lower() or ql in n.get("term","").lower() or ql in n.get("term_zh","").lower() or ql in n.get("人话摘要","").lower()]
    return {"count": len(nodes), "nodes": nodes}


@app.get("/api/nodes/{node_id}")
def get_node(node_id: str):
    data = load()
    node = next((n for n in data["nodes"] if n["id"] == node_id), None)
    if not node: raise HTTPException(404, f"Node {node_id} not found")
    deps   = [e for e in data["edges"] if e["source"] == node_id]
    dep_by = [e for e in data["edges"] if e["target"] == node_id]
    articles = load_articles().get("entity_articles", {}).get(node_id, [])
    return {"node": node, "depends_on": deps, "depended_by": dep_by, "articles": articles}


@app.get("/api/edges")
def list_edges(relation: str = None, source: str = None, target: str = None):
    data = load()
    edges = data["edges"]
    if relation: edges = [e for e in edges if e["relation"] == relation]
    if source:   edges = [e for e in edges if e["source"] == source]
    if target:   edges = [e for e in edges if e["target"] == target]
    return {"count": len(edges), "edges": edges}


@app.get("/api/articles")
def list_articles(node_id: str = None):
    """文章引用列表。?node_id=xxx 过滤某实体的相关文章；省略返回全部文章。"""
    art_data = load_articles()
    if node_id:
        arts = art_data.get("entity_articles", {}).get(node_id, [])
        return {"count": len(arts), "articles": arts}
    arts = art_data.get("articles", [])
    return {"count": len(arts), "articles": arts}


@app.get("/api/search")
def search(q: str = Query(..., min_length=1)):
    data = load()
    ql = q.lower()
    nodes = [n for n in data["nodes"] if ql in n["id"].lower() or ql in n.get("term","").lower() or ql in n.get("term_zh","").lower() or ql in n.get("人话摘要","").lower()]
    return {"query": q, "count": len(nodes), "nodes": nodes}


@app.get("/api/stats")
def stats():
    data = load()
    return data.get("meta", {})


@app.get("/api/health")
def health():
    data = load()
    return {"status": "ok", "nodes": len(data["nodes"]), "edges": len(data["edges"]), "updated": data.get("meta",{}).get("generated_at","")}
