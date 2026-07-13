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

import re

def _ref_exists(ref, ids):
    """检查引用是否存在。支持子约束引用（PHY-003-a → PHY-003）。"""
    if ref in ids:
        return True
    # 尝试去掉尾部 -[a-z] 后缀（子约束引用）
    base = re.sub(r"-[a-z]$", "", ref)
    return base in ids

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
            if isinstance(v, str) and v and not _ref_exists(v, ids):
                errs.append(f"{eid}: {k}='{v}' 不存在")
        for k in list_fields:
            for v in (e.get(k) or []):
                if isinstance(v, str) and not _ref_exists(v, ids):
                    errs.append(f"{eid}: {k} 引用 '{v}' 不存在")
        # depends_on: 扁平列表（概念）或嵌套 dict（定理/公理）
        deps = e.get("depends_on")
        if isinstance(deps, list):
            for v in deps:
                if isinstance(v, str) and not _ref_exists(v, ids):
                    errs.append(f"{eid}: depends_on 引用 '{v}' 不存在")
        elif isinstance(deps, dict):
            for sub_k in ("concepts", "l0_constraints", "axioms", "theorems"):
                for v in (deps.get(sub_k) or []):
                    if isinstance(v, str) and not _ref_exists(v, ids):
                        errs.append(f"{eid}: depends_on.{sub_k} 引用 '{v}' 不存在")
        # bridges_to: L2 桥接命题引用 L1 实体
        bridges = e.get("bridges_to")
        if isinstance(bridges, dict):
            for sub_k in ("concepts", "axioms", "theorems"):
                for v in (bridges.get(sub_k) or []):
                    if isinstance(v, str) and not _ref_exists(v, ids):
                        errs.append(f"{eid}: bridges_to.{sub_k} 引用 '{v}' 不存在")
    for e in errs: print(f"❌ {e}")
    print("✅ 引用完整性: 通过" if not errs else "")
    return errs


def check_circular_deps(es):
    """检测定理间的循环依赖。"""
    # 构建定理依赖图：theorem_id → {依赖的定理 IDs}
    g = {}
    for p, e in es.items():
        eid = e.get("id", "")
        if not eid.startswith("THEOREM-"):
            continue
        deps = e.get("depends_on", {})
        if isinstance(deps, dict):
            g[eid] = set(deps.get("theorems", []))
        else:
            g[eid] = set()

    # DFS 检测循环
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in g}
    cycle = []

    def dfs(n, path):
        color[n] = GRAY
        for m in g.get(n, set()):
            if m not in color:
                continue  # 引用了不存在的定理（由 check_refs 报告）
            if color[m] == GRAY:
                # 找到循环：从 path 中 m 的位置开始
                idx = path.index(m) if m in path else 0
                cycle.extend(path[idx:] + [m])
                return True
            if color[m] == WHITE:
                if dfs(m, path + [m]):
                    return True
        color[n] = BLACK
        return False

    for n in g:
        if color[n] == WHITE:
            if dfs(n, [n]):
                break

    if cycle:
        chain = " → ".join(cycle)
        print(f"❌ 循环依赖: {chain}")
        return [f"循环依赖: {chain}"]

    print("✅ 无循环依赖")
    return []

def check_status(es):
    errs = []
    valid_l2_status = {"candidate", "verified", "weakly_verified", "rejected"}
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
        if "L2-bridging" in p:
            st = e.get("status", "")
            if st not in valid_l2_status:
                errs.append(f"{eid}: status='{st}' 无效 (需为 candidate|verified|weakly_verified|rejected)")
            if st == "verified":
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
    errs = check_ids(es) + check_refs(es) + check_circular_deps(es) + check_status(es)
    print(f"\n{'='*40}")
    if errs: print(f"❌ {len(errs)} 个错误"); sys.exit(1)
    else: print("✅ 全部通过")

if __name__ == "__main__": main()
