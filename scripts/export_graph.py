#!/usr/bin/env python3
"""
Export the human-society axiomatic system to graph-data.js for D3.js visualization.

Reads all YAML entity files across 5 layers, extracts nodes and edges,
and writes visualization/graph-data.js (and graph-data.json for reference).

Usage:
    python scripts/export_graph.py
"""

import yaml
import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIS_DIR = PROJECT_ROOT / "visualization"

LAYER_CONFIG = {
    "L0-physical": {
        "pattern": "L0-physical/constraints/*.yaml",
        "type": "physical_constraint",
        "layer": "L0",
        "layer_label": "物理约束",
    },
    "L1-definitions/concepts": {
        "pattern": "L1-definitions/concepts/*.yaml",
        "type": "concept",
        "layer": "L1",
        "layer_label": "定义层",
    },
    "L1-definitions/axioms": {
        "pattern": "L1-definitions/axioms/*.yaml",
        "type": "definitional_axiom",
        "layer": "L1",
        "layer_label": "定义层",
    },
    "L1-definitions/theorems": {
        "pattern": "L1-definitions/theorems/*.yaml",
        "type": "theorem",
        "layer": "L1",
        "layer_label": "定义层",
    },
    "L2-bridging": {
        "pattern": "L2-bridging/**/*.yaml",
        "type": "bridging_proposition",
        "layer": "L2",
        "layer_label": "桥接层",
    },
    "L3-deductions": {
        "pattern": "L3-deductions/corollaries/*.yaml",
        "type": "deduction",
        "layer": "L3",
        "layer_label": "推论层",
    },
    "L4-composites": {
        "pattern": "L4-composites/corollaries/*.yaml",
        "type": "composite_deduction",
        "layer": "L4",
        "layer_label": "复合推论层",
    },
}

EXCLUDE_DIRS = {"reviews", "empirical-tests", "cross-verification"}


def normalize_id(raw_id: str) -> str:
    """Normalize entity IDs: strip sub-clause suffixes like PHY-003-b -> PHY-003."""
    m = re.match(r"^(PHY-\d+)-[a-z]$", raw_id)
    if m:
        return m.group(1)
    return raw_id


def extract_ids_from_value(value) -> list:
    """Extract entity IDs from list or list-of-dicts."""
    ids = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                ids.append(normalize_id(item))
            elif isinstance(item, dict):
                for k in item:
                    ids.append(normalize_id(k))
    elif isinstance(value, dict):
        for k in value:
            ids.append(normalize_id(k))
    return ids


def extract_edges_from_depends_on(depends_on, relation: str) -> list:
    """Extract edges from a depends_on field (flat list or structured dict)."""
    edges = []
    if isinstance(depends_on, list):
        for item in depends_on:
            if isinstance(item, str):
                edges.append({"target": normalize_id(item), "relation": relation})
            elif isinstance(item, dict):
                for k in item:
                    edges.append({"target": normalize_id(k), "relation": relation})
    elif isinstance(depends_on, dict):
        for sub_key, id_list in depends_on.items():
            if isinstance(id_list, list):
                for item in id_list:
                    if isinstance(item, str):
                        edges.append({"target": normalize_id(item), "relation": relation})
                    elif isinstance(item, dict):
                        for k in item:
                            edges.append({"target": normalize_id(k), "relation": relation})
            elif isinstance(id_list, dict):
                for k in id_list:
                    edges.append({"target": normalize_id(k), "relation": relation})
    return edges


def extract_all_edges(entity_id: str, data: dict) -> list:
    """Extract all outgoing edges from an entity's YAML data."""
    edges = []
    if "depends_on" in data and data["depends_on"] is not None:
        edges.extend(extract_edges_from_depends_on(data["depends_on"], "depends_on"))
    if "bridges_to" in data and data["bridges_to"] is not None:
        edges.extend(extract_edges_from_depends_on(data["bridges_to"], "bridges_to"))
    if "derived_from_concepts" in data and data["derived_from_concepts"] is not None:
        edges.extend(extract_edges_from_depends_on(data["derived_from_concepts"], "derived_from"))
    if "l0_grounding" in data and data["l0_grounding"] is not None:
        edges.extend(extract_edges_from_depends_on(data["l0_grounding"], "grounded_in"))
    if "l0_constraints" in data and data["l0_constraints"] is not None:
        edges.extend(extract_edges_from_depends_on(data["l0_constraints"], "grounded_in"))
    # derivation.from_l1 / from_l2 — used by L3/L4 deductions
    derivation = data.get("derivation")
    if isinstance(derivation, dict):
        for level_key in ("from_l1", "from_l2", "from_l3"):
            level = derivation.get(level_key)
            if isinstance(level, dict):
                for sub_key, id_list in level.items():
                    if isinstance(id_list, list):
                        for item in id_list:
                            if isinstance(item, str):
                                edges.append({"target": normalize_id(item), "relation": "depends_on"})
    return edges


def resolve_type(data: dict, dir_key: str) -> str:
    """Resolve canonical type from YAML data and directory."""
    t = data.get("type", "")
    if t == "composite_deduction":
        return "composite_deduction"
    if t == "deduction":
        if data.get("deduction_form") == "composite":
            return "composite_deduction"
        return "deduction"
    if t == "physical_constraint":
        return "physical_constraint"
    if t == "definitional_axiom":
        return "definitional_axiom"
    if t == "theorem":
        return "theorem"
    return LAYER_CONFIG[dir_key]["type"]


def split_term(term: str) -> tuple:
    """Split term into Chinese and English parts."""
    if not term:
        return "", ""
    term = term.strip()
    m = re.match(r"^(.+?)\s*\((.+?)\)$", term)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return term, ""


def parse_yaml_file(filepath: Path) -> dict | None:
    """Parse a YAML file, return dict or None on failure."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return None
        return data
    except Exception as e:
        print(f"  WARNING: Failed to parse {filepath}: {e}")
        return None


def export_articles(valid_node_ids: set):
    """Export articles.yaml → visualization/articles.js, return entity_articles for API."""
    articles_yaml = PROJECT_ROOT / "articles.yaml"
    if not articles_yaml.exists():
        print("  No articles.yaml found, skipping article export")
        return {}

    data = parse_yaml_file(articles_yaml)
    if data is None:
        return {}

    raw_articles = data.get("articles", [])
    if not isinstance(raw_articles, list):
        raw_articles = []

    # Build lookup: entity_id → [articles]
    entity_articles = {}
    valid_articles = []
    for art in raw_articles:
        if not isinstance(art, dict):
            continue
        url = art.get("url", "")
        title = art.get("title", "")
        date = str(art.get("date", ""))
        entity_ids = art.get("entity_ids", [])
        if not isinstance(entity_ids, list):
            entity_ids = []
        # Only keep references to valid node IDs
        valid_eids = [eid for eid in entity_ids if eid in valid_node_ids]
        if not url or not valid_eids:
            continue
        article_entry = {"url": url, "title": title, "date": date, "entity_ids": valid_eids}
        valid_articles.append(article_entry)
        for eid in valid_eids:
            entity_articles.setdefault(eid, []).append(article_entry)

    articles_output = {
        "articles": valid_articles,
        "entity_articles": entity_articles,
    }

    articles_js = VIS_DIR / "articles.js"
    json_str = json.dumps(articles_output, ensure_ascii=False, indent=2)
    with open(articles_js, "w", encoding="utf-8") as f:
        f.write(f"window.ARTICLE_DATA = {json_str};\n")
    print(f"  Wrote {articles_js} ({len(valid_articles)} articles, {len(entity_articles)} entities referenced)")
    return entity_articles


def main():
    print("Exporting human-society graph data...")

    nodes = []
    edges = []
    node_ids = set()
    type_counts = {}
    layer_counts = {}

    for dir_key, config in LAYER_CONFIG.items():
        pattern = config["pattern"]
        yaml_files = sorted(PROJECT_ROOT.glob(pattern))
        yaml_files = [f for f in yaml_files if not any(excl in f.parts for excl in EXCLUDE_DIRS)]

        for filepath in yaml_files:
            data = parse_yaml_file(filepath)
            if data is None:
                continue

            entity_id = data.get("id", filepath.stem)
            if not entity_id:
                continue

            canonical_type = resolve_type(data, dir_key)
            layer = config["layer"]
            layer_label = config["layer_label"]
            status = data.get("status", None)

            term = data.get("term", entity_id)
            term_zh, term_en = split_term(term)

            ren_hua = data.get("人话摘要", "")
            if isinstance(ren_hua, str):
                ren_hua = ren_hua.strip()
            statement = data.get("statement", "")
            if isinstance(statement, str):
                statement = statement.strip()

            domain = data.get("domain", [])
            if not isinstance(domain, list):
                domain = []

            created = data.get("created", "")
            revised = data.get("revised", "")

            node = {
                "id": entity_id,
                "term": term,
                "term_zh": term_zh or term,
                "type": canonical_type,
                "layer": layer,
                "layer_label": layer_label,
                "status": status,
                "人话摘要": ren_hua,
                "statement": statement,
                "domain": domain,
                "created": str(created) if created else "",
                "revised": str(revised) if revised else "",
            }
            nodes.append(node)
            node_ids.add(entity_id)

            type_counts[canonical_type] = type_counts.get(canonical_type, 0) + 1
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

            entity_edges = extract_all_edges(entity_id, data)
            for e in entity_edges:
                e["source"] = entity_id
            edges.extend(entity_edges)

    # Deduplicate edges
    relation_labels = {
        "depends_on": "依赖",
        "bridges_to": "桥接",
        "derived_from": "导出",
        "grounded_in": "基于",
    }

    unique_edges = []
    seen = set()
    for e in edges:
        key = (e["source"], e["target"], e["relation"])
        if key not in seen:
            seen.add(key)
            e["relation_label"] = relation_labels.get(e["relation"], e["relation"])
            unique_edges.append(e)

    valid_edges = [e for e in unique_edges if e["target"] in node_ids]

    # Compute degree
    out_degree = {}
    in_degree = {}
    for node in nodes:
        nid = node["id"]
        out_degree[nid] = sum(1 for e in valid_edges if e["source"] == nid)
        in_degree[nid] = sum(1 for e in valid_edges if e["target"] == nid)

    for node in nodes:
        node["depends_on_count"] = out_degree.get(node["id"], 0)
        node["depended_by_count"] = in_degree.get(node["id"], 0)

    output = {
        "nodes": nodes,
        "edges": valid_edges,
        "meta": {
            "total_nodes": len(nodes),
            "total_edges": len(valid_edges),
            "generated_at": datetime.now().isoformat(),
            "layers": layer_counts,
            "types": type_counts,
        },
    }

    VIS_DIR.mkdir(parents=True, exist_ok=True)

    # Export article references (included in graph-data JSON / API)
    entity_articles = export_articles(node_ids)
    if entity_articles:
        output["entity_articles"] = entity_articles

    js_path = VIS_DIR / "graph-data.js"
    json_str = json.dumps(output, ensure_ascii=False, indent=2)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(f"window.GRAPH_DATA = {json_str};\n")
    print(f"  Wrote {js_path}")

    json_path = VIS_DIR / "graph-data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  Wrote {json_path}")

    skipped = len(unique_edges) - len(valid_edges)
    print(f"\nDone! {len(nodes)} nodes, {len(valid_edges)} edges.")
    if skipped:
        print(f"  Skipped {skipped} edges with missing targets.")
    print(f"\nBy layer:")
    for layer in sorted(layer_counts.keys()):
        print(f"  {layer}: {layer_counts[layer]} nodes")
    print(f"\nBy type:")
    for t in sorted(type_counts.keys()):
        print(f"  {t}: {type_counts[t]} nodes")


if __name__ == "__main__":
    main()
