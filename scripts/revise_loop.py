#!/usr/bin/env python3
"""revise_loop.py - Review-Revise-Finalize loop 编排(无 Workflow 工具时清存量用)。

复刻 ded_pipeline/l4_pipeline 的 Phase 2-3 逻辑:
  每轮先看审查档当前 round 是否已审 -> 未审则 Review(review_minimax.py, MiniMax-M3
  异血统) -> 判 verdict ->
    verified     -> finalize.py(Q2 反例猎捕硬门校验)
    rejected     -> 停(上报主循环)
    needs_revision + fixes -> flash_revise.py(--mode patch --cross-check) -> 下一轮
    needs_revision 无 fixes -> 停(卡住,交主循环)
  最多 max_rounds 轮。

实体 YAML 必须已存在(candidate, 等价 workflow 的 skipAuthor 模式)。
本脚本只编排+守门,审查推理由 review_minimax.py 调 MiniMax-M3 完成(异血统独立,
主循环不当审查者,符合防自欺结构)。

用法:
    # 从未审查的 candidate(自动从 round_1 开始)
    python scripts/revise_loop.py L4-016 --layer L4 --review-num L4-016
    python scripts/revise_loop.py DED-039 --layer L3 --review-num 044

    # 已有 round_1 的(自动接手: Revise round_1 -> Review round_2 -> ...)
    python scripts/revise_loop.py L4-014 --layer L4 --review-num L4-014

输出 JSON 到 stdout(供主循环消费): {entity, result, rounds, chain, oneline}
  result: verified | rejected | stuck_no_fixes | max_rounds_reached |
          review_failed | revise_failed | finalize_failed
"""

import sys
import json
import subprocess
import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

LAYER_DIR = {"L4": "L4-composites", "L3": "L3-deductions", "L2": "L2-bridging"}


def review_path_for(entity_id, review_num, layer):
    """构造审查档相对路径(兼容三命名)。"""
    d = f"{LAYER_DIR[layer]}/reviews"
    if layer == "L2":
        return f"{d}/ADV-REVIEW-{entity_id}.yaml"
    return f"{d}/ADV-REVIEW-{review_num}-{entity_id}.yaml"


def read_round(review_full, rnd):
    """读审查档指定 round 块的 (verdict, fixes[])。无则 (None, [])。"""
    if not review_full.exists():
        return None, [], ""
    txt = review_full.read_text(encoding="utf-8")
    matches = list(re.finditer(rf"^round_{rnd}:\s*\n((?:.*\n)*?)(?=^round_\d+:|\Z)", txt, re.M))
    if not matches:
        return None, [], ""
    block = matches[-1].group(1)  # 取最后一个(处理重复 round_N)
    vm = re.search(r"verdict:\s*(\S+)", block)
    verdict = vm.group(1) if vm else None
    # required_fixes: YAML 列表(- "...") 或 []
    if re.search(r"required_fixes:\s*\[\s*\]", block):
        fixes = []
    else:
        fm = re.search(r"required_fixes:\s*\n((?:[ \t]+- .*\n)+)", block)
        if fm:
            fixes = [re.sub(r'^[ \t]+- "', "", ln).rstrip('"\n').replace('\\"', '"')
                     for ln in fm.group(1).split("\n") if ln.strip()]
        else:
            fixes = []
    # oneline(块标量,合并去换行)
    om = re.search(r"oneline:\s*\|?\s*\n((?:[ \t]+.*\n)*)", block)
    oneline = re.sub(r"\s+", " ", om.group(1)).strip() if om else ""
    return verdict, fixes, oneline


def entity_revised_for_round(entity_id, rnd):
    """检测实体是否已被 round rnd revise(review_summary 含 round 标记)。

    用于崩溃恢复:revise_loop 重跑时跳过已完成的 Revise,避免重复改实体。
    sensenova/flash 追加的 review_summary 含 'round {rnd}' 或 'r{rnd}' 标记。
    """
    for d in ["L3-deductions/corollaries", "L4-composites/corollaries",
              "L2-bridging/verified", "L2-bridging/weakly_verified", "L2-bridging/candidate"]:
        full = REPO / d
        if not full.exists():
            continue
        for f in sorted(full.glob(f"{entity_id}*.yaml")):
            txt = f.read_text(encoding="utf-8")
            m = re.search(r"^review_summary:.*?(?=^\S)", txt, re.M | re.S)
            if not m:
                return False
            block = m.group(0)[:3000]
            return (f"r{rnd} needs_revision" in block or f"r{rnd} ->" in block
                    or f"r{rnd}->" in block or f"round {rnd} needs_revision" in block)
    return False


def all_round_verdicts(review_full):
    """读审查档各轮 (n, verdict)。"""
    if not review_full.exists():
        return []
    txt = review_full.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^round_(\d+):\s*\n((?:.*\n)*?)(?=^round_\d+:|\Z)", txt, re.M):
        vm = re.search(r"verdict:\s*(\S+)", m.group(2))
        out.append((int(m.group(1)), vm.group(1) if vm else "?"))
    return out


def run(cmd):
    """跑子进程,返回 (rc, stdout, stderr)。"""
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def main():
    ap = argparse.ArgumentParser(description="Review-Revise-Finalize loop 编排(清存量)")
    ap.add_argument("entity_id", help="推论 id (L4-016 / DED-039 / BR-L2-025)")
    ap.add_argument("--layer", required=True, choices=["L3", "L4", "L2"])
    ap.add_argument("--review-num", required=True,
                    help="ADV-REVIEW 编号 (L4=L4-016, L3=044, L2=BR-L2-010)")
    ap.add_argument("--max-rounds", type=int, default=3)
    args = ap.parse_args()

    rpath = review_path_for(args.entity_id, args.review_num, args.layer)
    rfull = REPO / rpath

    # 确定起始轮:审查档最大轮(从接手)或 1(新审)
    existing = [n for n, _ in all_round_verdicts(rfull)]
    round = max(existing) if existing else 1
    oneline = ""

    print(f"📋 {args.entity_id} layer={args.layer} review={rpath} "
          f"start_round={round} max={args.max_rounds}", file=sys.stderr)

    while round <= args.max_rounds:
        # ── 当前 round 是否已审 ──
        verdict, fixes, oneline = read_round(rfull, round)

        if verdict is None:
            # 未审 -> Review(minimax 偶发格式失败,重试1次)
            rev = None
            for attempt in (1, 2):
                tag = "" if attempt == 1 else f" (重试{attempt})"
                print(f"\n=== round {round}: Review (MiniMax-M3 异血统){tag} ===",
                      file=sys.stderr)
                rc, out, err = run(["python", "scripts/review_minimax.py", args.entity_id,
                                    "--review-round", str(round),
                                    "--review-path", rpath, "--layer", args.layer])
                if rc != 0:
                    if attempt == 1:
                        print(f"   ⚠️ rc={rc},重试...", file=sys.stderr); continue
                    print(json.dumps({"entity": args.entity_id, "result": "review_failed",
                          "round": round, "stderr": (err or out)[-300:]},
                         ensure_ascii=False)); return
                try:
                    rev = json.loads(out)
                except Exception:
                    if attempt == 1:
                        print(f"   ⚠️ JSON 解析失败,重试...", file=sys.stderr); continue
                    print(json.dumps({"entity": args.entity_id, "result": "review_failed",
                          "round": round, "raw": out[:300]}, ensure_ascii=False)); return
                if rev.get("done") and rev.get("validatorOk"):
                    break
                if attempt == 1:
                    print(f"   ⚠️ {(rev.get('note') or '')[:60]},重试...", file=sys.stderr); continue
                print(json.dumps({"entity": args.entity_id, "result": "review_failed",
                      "round": round, "note": rev.get("note", "")}, ensure_ascii=False)); return
            verdict = rev.get("verdict", "")
            fixes = rev.get("requiredFixes", [])
            oneline = rev.get("oneline", "")
            print(f"   verdict={verdict} fixes={len(fixes)} oneline={oneline[:80]}",
                  file=sys.stderr)
        else:
            print(f"\n=== round {round}: 已审 verdict={verdict} fixes={len(fixes)} ===",
                  file=sys.stderr)

        # ── 判 verdict ──
        if verdict == "verified":
            rvs = all_round_verdicts(rfull)
            chain = " -> ".join(f"r{n} {v}" for n, v in rvs) or f"r{round} verified"
            print(f"\n=== Finalize (Q2 反例猎捕硬门) chain={chain} ===", file=sys.stderr)
            rc, out, err = run(["python", "scripts/finalize.py", args.entity_id,
                                "--verdict", "verified", "--chain", chain,
                                "--why", oneline,
                                "--review-num", args.review_num, "--no-index"])
            if out: print(out, file=sys.stderr)
            if err: print(err, file=sys.stderr)
            if rc != 0:
                result = {"entity": args.entity_id, "result": "finalize_failed",
                          "round": round, "stdout": out[-400:]}
                print(json.dumps(result, ensure_ascii=False)); return
            result = {"entity": args.entity_id, "result": "verified", "rounds": round,
                      "chain": chain, "oneline": oneline}
            print(json.dumps(result, ensure_ascii=False)); return

        if verdict == "rejected":
            result = {"entity": args.entity_id, "result": "rejected", "round": round,
                      "oneline": oneline}
            print(json.dumps(result, ensure_ascii=False)); return

        # needs_revision
        if not fixes:
            print(f"⚠️  round {round}: needs_revision 但无 required,停(交主循环裁量)",
                  file=sys.stderr)
            result = {"entity": args.entity_id, "result": "stuck_no_fixes", "round": round,
                      "oneline": oneline}
            print(json.dumps(result, ensure_ascii=False)); return

        # ── Revise(flash_revise patch) ──
        # 幂等:实体已含 round_N revise 标记则跳过(崩溃恢复)
        if entity_revised_for_round(args.entity_id, round):
            print(f"   round {round}: 实体已 revise(review_summary 含 round {round} 标记),"
                  f"跳过 Revise,进 round {round+1}", file=sys.stderr)
            round += 1
            continue
        fixes_arg = " ||| ".join(fixes)
        print(f"\n=== round {round}: Revise (flash patch --cross-check, {len(fixes)} fixes) ===",
              file=sys.stderr)
        # Revise: patch 模式(失败回退 overwrite,处理列表索引等 patch 不支持的字段)
        rev2 = None
        for mode in ("patch", "overwrite"):
            rc, out, err = run(["python", "scripts/flash_revise.py", args.entity_id,
                                "--mode", mode, "--provider", "sensenova",
                                "--fixes", fixes_arg,
                                "--review-round", str(round), "--review-path", rpath])
            if rc != 0:
                if mode == "patch":
                    print(f"   ⚠️ patch rc={rc},回退 overwrite", file=sys.stderr); continue
                print(json.dumps({"entity": args.entity_id, "result": "revise_failed",
                      "round": round, "stderr": (err or out)[-300:]}, ensure_ascii=False)); return
            try:
                rev2 = json.loads(out)
            except Exception:
                if mode == "patch":
                    print(f"   ⚠️ patch JSON 失败,回退 overwrite", file=sys.stderr); continue
                print(json.dumps({"entity": args.entity_id, "result": "revise_failed",
                      "round": round, "raw": out[:300]}, ensure_ascii=False)); return
            if rev2.get("done") and rev2.get("validatorOk"):
                break
            if mode == "patch":
                print(f"   ⚠️ patch 失败({(rev2.get('note') or '')[:50]}),回退 overwrite",
                      file=sys.stderr); continue
            print(json.dumps({"entity": args.entity_id, "result": "revise_failed",
                  "round": round, "note": rev2.get("note", "")}, ensure_ascii=False)); return
        print(f"   ✓ revise ok ({'patch' if rev2.get('patchFields') else 'overwrite'}): "
              f"{(rev2.get('note') or '')[:70]}", file=sys.stderr)
        round += 1

    # 达 max_rounds
    rvs = all_round_verdicts(rfull)
    chain = " -> ".join(f"r{n} {v}" for n, v in rvs)
    print(f"⚠️  达 max_rounds={args.max_rounds},停(未 verified)", file=sys.stderr)
    result = {"entity": args.entity_id, "result": "max_rounds_reached",
              "rounds": args.max_rounds, "chain": chain}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
