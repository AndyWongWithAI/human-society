#!/usr/bin/env python3
"""run_pipeline.py - 全链路 Python 串联(去包裹层 plan 措施2)。

替代 ded_pipeline.workflow.js / l4_pipeline.workflow.js 的 workflow agent 编排。
薄编排: author_pro.py(Author) -> revise_loop.py(Review-Revise-Finalize)。不重新实现
审查/整改/定论, 全部委托 L1 原子脚本, 去掉 7 个 glm-5.2 包裹层 workflow agent。

分层(L2 编排引用 L1 原子, 不重写):
  L1: author_draft.py / author_pro.py / review_minimax.py / flash_revise.py / finalize.py
  L2: revise_loop.py(Phase 2-3 编排) / run_pipeline.py(全链路薄编排, 本脚本)

用法:
    python scripts/run_pipeline.py --brief-file /tmp/brief.json \\
        --layer L3 --review-num 055 [--freeDraft] [--max-rounds 3]

输出(stdout, 一行 JSON, 与 ded_pipeline.workflow.js 返回结构兼容):
    {"id":"DED-055","verdict":"verified","rounds":2,"dedPath":"...","reviewPath":"...",
     "core":"...","authorTokens":33496}
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(cmd):
    """跑子进程, 返回 (rc, stdout, stderr)。"""
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def parse_json_out(out):
    """从脚本 stdout 解析最后一行 JSON(脚本可能先打印 stderr 进度, stdout 只输出 JSON)。"""
    for line in reversed(out.strip().split("\n")):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except Exception:
                continue
    return None


def main():
    ap = argparse.ArgumentParser(description="全链路 Python 串联(去包裹层 plan 措施2)")
    ap.add_argument("--brief-file", required=True, help="brief JSON 文件路径")
    ap.add_argument("--layer", required=True, choices=["L3", "L4"])
    ap.add_argument("--review-num", required=True,
                    help="ADV-REVIEW 编号 (L3=055, L4=L4-020)")
    ap.add_argument("--freeDraft", action="store_true",
                    help="先用免费模型出骨架, 再 author_pro 编辑(省 30-50%% Author token)")
    ap.add_argument("--max-rounds", type=int, default=3)
    args = ap.parse_args()

    with open(args.brief_file) as f:
        brief = json.load(f)
    entity_id = brief.get("id", "?")

    print(f"🚀 run_pipeline {entity_id} layer={args.layer} "
          f"freeDraft={args.freeDraft} max_rounds={args.max_rounds}", file=sys.stderr)

    # ============ Phase 1: Author ============
    draft_arg = []
    if args.freeDraft:
        print("\n=== Phase 1a: freeDraft 骨架(免费模型, reasoning_effort=none) ===",
              file=sys.stderr)
        rc, out, err = run(["python", "scripts/author_draft.py",
                            "--brief-file", args.brief_file])
        if err:
            print(err, file=sys.stderr)
        d = parse_json_out(out)
        if d and d.get("done") and d.get("draftPath"):
            draft_arg = ["--draft", d["draftPath"]]
            print(f"   ✓ 骨架: {d['draftPath']}", file=sys.stderr)
        else:
            print(f"   ⚠️ freeDraft 失败, author_pro 从零创作: "
                  f"{(d or {}).get('note', out[:150])}", file=sys.stderr)

    print("\n=== Phase 1: Author(glm-5.2 Python 直调, reasoning_effort=high) ===",
          file=sys.stderr)
    rc, out, err = run(["python", "scripts/author_pro.py",
                        "--brief-file", args.brief_file,
                        "--layer", args.layer] + draft_arg)
    if err:
        print(err, file=sys.stderr)
    authored = parse_json_out(out)
    if not authored or not authored.get("done") or not authored.get("validatorOk"):
        result = {"id": entity_id, "verdict": "author_failed", "rounds": 0,
                  "note": (authored or {}).get("note", out[-300:])}
        print(json.dumps(result, ensure_ascii=False))
        return
    ded_path = authored.get("draftPath", "")
    author_tokens = authored.get("usage", {}).get("total_tokens")
    print(f"   ✓ Author 完成: {ded_path} (attempts={authored.get('attempts')}, "
          f"tokens={author_tokens})", file=sys.stderr)

    # ============ Phase 2-3: Review-Revise-Finalize (委托 revise_loop) ============
    print(f"\n=== Phase 2-3: revise_loop(Review minimax 异血统 -> Revise 免费 -> Finalize 脚本) ===",
          file=sys.stderr)
    rc, out, err = run(["python", "scripts/revise_loop.py", entity_id,
                        "--layer", args.layer,
                        "--review-num", args.review_num,
                        "--max-rounds", str(args.max_rounds)])
    if err:
        print(err, file=sys.stderr)
    loop = parse_json_out(out)
    if not loop:
        result = {"id": entity_id, "verdict": "loop_failed", "rounds": 0,
                  "dedPath": ded_path, "note": out[-300:]}
        print(json.dumps(result, ensure_ascii=False))
        return

    result_str = loop.get("result", "unknown")
    rounds = loop.get("rounds", 0)
    chain = loop.get("chain", "")
    oneline = loop.get("oneline", "")

    # 映射 result -> verdict(与 ded_pipeline.workflow.js 返回兼容)
    verdict_map = {
        "verified": "verified",
        "rejected": "rejected",
        "stuck_no_fixes": "needs_revision",
        "max_rounds_reached": "needs_revision",
        "review_failed": "review_failed",
        "revise_failed": "revise_failed",
        "finalize_failed": "finalize_failed",
    }
    verdict = verdict_map.get(result_str, result_str)

    layer_dir = "L4-composites" if args.layer == "L4" else "L3-deductions"
    review_path = f"{layer_dir}/reviews/ADV-REVIEW-{args.review_num}-{entity_id}.yaml"

    print(f"\n=== 结果: {verdict} (rounds={rounds}) chain={chain} ===", file=sys.stderr)

    print(json.dumps({
        "id": entity_id,
        "verdict": verdict,
        "result": result_str,
        "rounds": rounds,
        "chain": chain,
        "core": brief.get("coreClaim", brief.get("title", "")),
        "counterexample": "",
        "dedPath": ded_path,
        "reviewPath": review_path,
        "oneline": oneline,
        "authorTokens": author_tokens,
        "next": "主循环:校验已过, git add 两文件并提交(按授权自主提交)" if verdict == "verified"
                else ("主循环:上报 rejected + 归档" if verdict == "rejected"
                      else "主循环:needs_revision 未收敛, 人工裁量"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
