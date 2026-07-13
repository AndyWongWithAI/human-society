#!/usr/bin/env python3
"""validate.py — 一致性校验"""
import sys, yaml
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"iterations", ".git", "__pycache__", "docs"}

def load():
    es = {}
    for f in ROOT.rglob("*.yaml"):
        if any(d in f.parts for d in SKIP): continue
        if f.name in ("independence-model.yaml", "META.yaml"): continue
        try:
            with open(f) as fh: d = yaml.safe_load(fh)
            if d and isinstance(d, dict) and "id" in d:
                es[str(f.relative_to(ROOT))] = d
        except yaml.YAMLError as e:
            print(f"❌ YAML: {f.relative_to(ROOT)}: {e}")
    return es

def check_ids(es):
    m = defaultdict(list)
    for p, e in es.items(): m[e["id"]].append(p)
    errs = [f"ID 重复: '{i}' -> {ps}" for i, ps in m.items() if len(ps) > 1]
    for e in errs: print(f"❌ {e}")
    print(f"✅ ID 唯一性: {len(es)} 实体" if not errs else "")
    return errs

def check_refs(es):
    ids = set(e["id"] for e in es.values())
    ref_fields = ["bridges_to_concept", "target_bridging", "source_id",
                  "primary_suspect", "secondary_suspect", "unlikely_suspect"]
    list_fields = ["depends_on_l0", "supports_bridging", "conflicts_with",
                   "l0_axioms", "l1_bridging"]
    errs = []
    for p, e in es.items():
        eid = e.get("id", "?")
        for k in ref_fields:
            v = e.get(k)
            if isinstance(v, str) and v and v not in ids:
                errs.append(f"{eid}: {k}='{v}' 不存在")
        for k in list_fields:
            for v in (e.get(k) or []):
                if isinstance(v, str) and v not in ids:
                    errs.append(f"{eid}: {k} 引用 '{v}' 不存在")
    for e in errs: print(f"❌ {e}")
    print("✅ 引用完整性: 通过" if not errs else "")
    return errs

def check_status(es):
    errs = []
    for p, e in es.items():
        eid = e.get("id", "?")
        if "L3-deductions/corollaries" in p:
            if not e.get("falsification_trace", {}).get("primary_suspect"):
                errs.append(f"{eid}: 缺少 falsification_trace.primary_suspect")
            if not e.get("real_world_anchors"):
                errs.append(f"{eid}: 缺少 real_world_anchors")
        if "L1-definitions/axioms" in p:
            nt = e.get("negation_test", {})
            if nt.get("verdict") not in ("passes", "fails", "contested"):
                errs.append(f"{eid}: negation_test.verdict 缺失/无效")
        if "L2-bridging" in p and e.get("status") == "verified":
            cv = e.get("cross_verification", {})
            iea = cv.get("iea")
            if iea is not None and iea < 1.2:
                errs.append(f"{eid}: IEA={iea} 但状态为 verified (需 ≥1.2)")
    for e in errs: print(f"❌ {e}")
    print("✅ 状态检查: 通过" if not errs else "")
    return errs

def main():
    print("=" * 40 + "\n一致性校验\n" + "=" * 40)
    es = load()
    if not es: print("\n尚无实体。"); return
    print(f"\n{len(es)} 个实体\n")
    errs = check_ids(es) + check_refs(es) + check_status(es)
    print(f"\n{'='*40}")
    if errs: print(f"❌ {len(errs)} 个错误"); sys.exit(1)
    else: print("✅ 全部通过")

if __name__ == "__main__": main()
