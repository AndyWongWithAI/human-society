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
            for sub_k in ("concepts", "l0_constraints", "axioms", "theorems", "bridging", "deductions", "composite_deductions"):
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
    """检测推导依赖的循环：定理→定理、推论→推论(Rule D)。"""
    # 构建依赖图：entity_id → {它依赖的 定理/推论 IDs}
    # 覆盖 depends_on.theorems (L1) 与 depends_on.deductions (L3, Rule D)。
    g = {}
    for p, e in es.items():
        eid = e.get("id", "")
        if not eid:
            continue
        deps = e.get("depends_on", {})
        edges = set()
        if isinstance(deps, dict):
            edges |= set(deps.get("theorems", []) or [])
            edges |= set(deps.get("deductions", []) or [])
            edges |= set(deps.get("composite_deductions", []) or [])
        g[eid] = edges

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
    # Rule D/F confidence_floor：推论 id→status 映射 + 秩/上限表
    ded_status = {e.get("id", ""): e.get("status", "")
                  for p, e in es.items() if "L3-deductions/corollaries" in p}
    l4_status = {e.get("id", ""): e.get("status", "")
                 for p, e in es.items() if "L4-composites/corollaries" in p}
    RANK = {"verified": 4, "verified*": 3, "weakly_verified": 2, "candidate": 1, "rejected": 0}
    # 父状态给子推论施加的状态上限：rejected 父 → 子退回 candidate(不得 verified)
    CAP = {"verified": 4, "verified*": 3, "weakly_verified": 2, "candidate": 1, "rejected": 1}
    all_ded_status = {**ded_status, **l4_status}
    for p, e in es.items():
        eid = e.get("id", "?")
        if "L3-deductions/corollaries" in p:
            st = e.get("status", "")
            if st not in ("candidate", "verified", "verified*", "weakly_verified", "rejected"):
                errs.append(f"{eid}: status='{st}' 无效 (需为 candidate|verified|verified*|weakly_verified|rejected)")
            if not e.get("falsification_trace", {}).get("primary_suspect"):
                errs.append(f"{eid}: 缺少 falsification_trace.primary_suspect")
            if not e.get("real_world_anchors"):
                errs.append(f"{eid}: 缺少 real_world_anchors")
            # Rule D: confidence_floor — 子推论状态不得高于任一父前提允许的上限
            deps = e.get("depends_on", {})
            parents = deps.get("deductions", []) if isinstance(deps, dict) else []
            caps = [(par, CAP[ded_status[par]], ded_status[par])
                    for par in (parents or [])
                    if par in ded_status and ded_status[par] in CAP]
            if caps:
                weakest = min(caps, key=lambda c: c[1])
                if RANK.get(st, 0) > weakest[1]:
                    errs.append(
                        f"{eid}: confidence_floor 违反 — status='{st}' 高于父前提 "
                        f"'{weakest[0]}'(status={weakest[2]}) 允许的上限")
            # 铁律：L3 推论不得引用 L4 实体
            l3_deps = e.get("depends_on", {})
            l4_refs = (l3_deps.get("composite_deductions", []) if isinstance(l3_deps, dict) else [])
            if l4_refs:
                errs.append(f"{eid}: L3 推论引用了 L4 实体 {l4_refs} —— 违反下层不依赖上层铁律")
        if "L4-composites/corollaries" in p:
            st = e.get("status", "")
            if st not in ("candidate", "verified", "verified*", "weakly_verified", "rejected"):
                errs.append(f"{eid}: status='{st}' 无效 (需为 candidate|verified|verified*|weakly_verified|rejected)")
            if not e.get("falsification_trace", {}).get("primary_suspect"):
                errs.append(f"{eid}: 缺少 falsification_trace.primary_suspect")
            if not e.get("real_world_anchors"):
                errs.append(f"{eid}: 缺少 real_world_anchors")
            if not e.get("emergence_demonstration"):
                errs.append(f"{eid}: 缺少 emergence_demonstration (L4 必须证明涌现)")
            if e.get("deduction_form") != "composite":
                errs.append(f"{eid}: deduction_form 必须为 'composite' (L4 固有)")
            # claim_type 合法值校验
            ct = e.get("claim_type")
            valid_ct = {"social_form_prediction", "trajectory_prediction", "phase_transition", "phase_diagram", "co_evolution", "mechanism_proposal", "structural_hypothesis", "bidirectional_dynamics"}
            if ct and ct not in valid_ct:
                errs.append(f"{eid}: claim_type='{ct}' 无效 (需为 {'|'.join(sorted(valid_ct))})")
            # 主前提：depends_on.deductions 必须 ≥2 条 L3 推论
            deps = e.get("depends_on", {})
            l3_parents = deps.get("deductions", []) if isinstance(deps, dict) else []
            if len(l3_parents) < 2:
                errs.append(f"{eid}: depends_on.deductions 至少需要 2 条 L3 推论作为主前提 (L4 硬门槛，当前 {len(l3_parents)} 条)")
            # confidence_floor：L4 status ≤ min(所有 L3+L4 父前提的 CAP)
            l4_parents = deps.get("composite_deductions", []) if isinstance(deps, dict) else []
            all_parents = l3_parents + l4_parents
            caps = [(par, CAP[all_ded_status[par]], all_ded_status[par])
                    for par in all_parents
                    if par in all_ded_status and all_ded_status[par] in CAP]
            if caps:
                weakest = min(caps, key=lambda c: c[1])
                if RANK.get(st, 0) > weakest[1]:
                    errs.append(
                        f"{eid}: confidence_floor 违反 — status='{st}' 高于父前提 "
                        f"'{weakest[0]}'(status={weakest[2]}) 允许的上限")
        # L1 公理/定理是分析性真理——必须携带 negation_test（否定它则话语崩溃的论证）。
        # 概念(CONCEPT-*)是定义、不可证伪，不做此检查。
        if "L1-definitions/axioms" in p or "L1-definitions/theorems" in p:
            nt = e.get("negation_test")
            if not nt:
                errs.append(f"{eid}: L1 公理/定理缺少 negation_test 字段")
        if "L1-definitions/axioms" in p:
            nt = e.get("negation_test") or {}
            if not isinstance(nt, dict) or nt.get("verdict") not in ("passes", "fails", "contested"):
                errs.append(f"{eid}: negation_test.verdict 缺失/无效")
        if "L2-bridging" in p and "reviews" not in p:
            st = e.get("status", "")
            if st not in valid_l2_status:
                errs.append(f"{eid}: status='{st}' 无效 (需为 candidate|verified|weakly_verified|rejected)")
            if st == "verified":
                cv = e.get("cross_verification", {})
                if isinstance(cv, dict):
                    iea = cv.get("iea")
                    if iea is not None and iea < 1.2:
                        errs.append(f"{eid}: IEA={iea} 但状态为 verified (需 ≥1.2)")
                elif cv:
                    errs.append(f"{eid}: cross_verification 非 dict(格式坏),无法校验 IEA")
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
