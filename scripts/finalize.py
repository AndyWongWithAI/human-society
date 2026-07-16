#!/usr/bin/env python3
"""翻牌最终化:status 翻转 + review_summary 压缩 + validate 校验。

替代管线中 finalize agent 的手工操作,避免 YAML 陷阱(缩进/ASCII冒号/静默丢失)。

用法:
    python scripts/finalize.py DED-031 --verdict verified \
        --chain "r1 needs_revision -> r2 verified" \
        --why "核心载重:考核切换前后差+核查成本弹性;两轮反例猎捕无活反例" \
        --review-num 038

    python scripts/finalize.py BR-L2-025 --verdict verified \
        --chain "r1 needs_revision -> r2 verified" \
        --why "IEA升至1.8:API操作化锚+独立折扣修正" \
        --review-num 039 \
        --note "IEA重算+独立折扣应用"

    python scripts/finalize.py DED-007 --verdict rejected \
        --chain "r1 rejected" \
        --why "测量轴焊死,无法靠改措辞救活" \
        --review-num 015

支持的状态转换:
    candidate       → verified | verified* | rejected
    weakly_verified → verified | rejected

脚本做的事:
    1. 按 ID 定位实体 YAML 文件
    2. 翻转 status 字段
    3. 用模板压缩/覆写 review_summary (≤3 行,| 块标量)
    4. 写入 revised 日期 + revision_note
    5. 跑 validate.py
    6. 可选:重生 INDEX.md
"""

import sys
import os
import subprocess
import argparse
import re
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SEARCH_DIRS = [
    "L3-deductions/corollaries",
    "L4-composites",
    "L2-bridging/verified",
    "L2-bridging/weakly_verified",
    "L2-bridging/candidate",
]

VALID_TRANSITIONS = {
    "candidate": ["verified", "verified*", "rejected"],
    "weakly_verified": ["verified", "rejected"],
    # weakly_verified 是 L2 标准状态,但部分早期 L3 推论(DED-033)也使用此状态
}


def find_entity(entity_id: str) -> Path | None:
    """按 ID 查找实体 YAML 文件。"""
    for search_dir in SEARCH_DIRS:
        full_dir = REPO / search_dir
        if not full_dir.exists():
            continue
        for f in sorted(full_dir.glob(f"{entity_id}*.yaml")):
            content = f.read_text(encoding="utf-8")
            if f"id: {entity_id}" in content:
                return f
    return None


def flip_status(lines: list[str], old: str, new: str) -> bool:
    """翻转 status 行(精确替换)。"""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("status:") and old in stripped:
            lines[i] = line.replace(f"status: {old}", f"status: {new}")
            return True
    return False


def upsert_review_summary(
    lines: list[str], chain: str, why: str, review_num: str
) -> None:
    """写入/覆写 review_summary(≤3 行,| 块标量)。"""
    template = (
        f"1) {chain}.\n"
        f"2) {why}.\n"
        f"3) 全档见 ADV-REVIEW-{review_num}。\n"
    )

    # 找到现有 review_summary 块的范围
    summary_start = None
    summary_end = None

    for i, line in enumerate(lines):
        if line.startswith("review_summary:"):
            summary_start = i
            if line.rstrip().endswith("|"):
                # 块标量 — 找到下一个顶层 key(列0,非空非注释)
                for j in range(i + 1, len(lines)):
                    if lines[j] and lines[j][0] not in (" ", "\t", "#", "\n"):
                        summary_end = j
                        break
                if summary_end is None:
                    summary_end = len(lines)
            else:
                # 行内标量 — 只替换这一行
                summary_end = i + 1
            break

    # 构建新的块标量
    new_lines = ["review_summary: |\n"]
    for tline in template.split("\n"):
        if tline:
            new_lines.append(f"  {tline}\n")

    if summary_start is not None:
        lines[summary_start:summary_end] = new_lines
    else:
        # 文件中没有 review_summary — 插到 depends_on/domain/created 之前
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.startswith(("depends_on:", "domain:", "created:")):
                insert_at = i
                break
        # 在前面加一个空行使 YAML 可读
        new_lines.insert(0, "\n")
        lines[insert_at:insert_at] = new_lines


def upsert_scalar(lines: list[str], key: str, value: str) -> None:
    """写入/覆写一个简单标量字段。"""
    for i, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            lines[i] = f"{key}: {value}\n"
            return

    # 不存在 — 插到 depends_on/domain 之前
    insert_at = len(lines)
    for i, line in enumerate(lines):
        if line.startswith(("depends_on:", "domain:")):
            insert_at = i
            break
    lines.insert(insert_at, f"{key}: {value}\n")


def detect_status(lines: list[str]) -> str | None:
    """从文件行中提取当前 status。"""
    for line in lines:
        m = re.match(r"^status:\s*(\S+)", line)
        if m:
            return m.group(1)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="翻牌最终化:status 翻转 + review_summary 压缩 + validate"
    )
    parser.add_argument("id", help="实体 ID (如 DED-031, BR-L2-025, L4-005)")
    parser.add_argument(
        "--verdict",
        required=True,
        choices=["verified", "verified*", "rejected"],
        help="目标定论",
    )
    parser.add_argument(
        "--chain",
        required=True,
        help='审查裁决链 (如 "r1 needs_revision -> r2 verified")',
    )
    parser.add_argument("--why", required=True, help="一句话:为何是这个定论")
    parser.add_argument(
        "--review-num", required=True, help="ADV-REVIEW 编号 (如 038)"
    )
    parser.add_argument("--note", default="", help="可选 revision_note(默认自动生成)")
    parser.add_argument(
        "--no-index", action="store_true", help="跳过 INDEX.md 重生"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只打印变更,不写入"
    )
    args = parser.parse_args()

    # ── 1. 查找实体 ──
    entity_path = find_entity(args.id)
    if not entity_path:
        print(f"❌ 找不到实体 {args.id}")
        sys.exit(1)

    # ── 2. 读取 + 探测状态 ──
    lines = open(entity_path, "r", encoding="utf-8").readlines()
    old_status = detect_status(lines)
    if old_status is None:
        print(f"❌ 找不到 status 字段")
        sys.exit(1)

    if old_status not in VALID_TRANSITIONS:
        print(
            f"❌ 当前 status={old_status},不支持通过 finalize 翻牌(可能已定论或被拒)"
        )
        sys.exit(1)

    if args.verdict not in VALID_TRANSITIONS[old_status]:
        print(f"❌ 不支持 {old_status} → {args.verdict} 转换")
        print(f"   合法转换: {VALID_TRANSITIONS[old_status]}")
        sys.exit(1)

    target_status = args.verdict
    today = date.today().isoformat()

    revision_note = args.note or (
        f"{today} finalize: status {old_status} → {target_status}。"
    )

    changes = [
        f"status: {old_status} → {target_status}",
        "review_summary → 模板压缩(≤3行)",
        f"revised: {today}",
        f"revision_note: {revision_note}",
    ]

    if args.dry_run:
        rel = entity_path.relative_to(REPO)
        print(f"📄 {rel}")
        for c in changes:
            print(f"   • {c}")
        print("   (dry-run, 未写入)")
        return

    # ── 3. 应用变更 ──
    if not flip_status(lines, old_status, target_status):
        print(f"❌ 翻转 status 失败(行匹配异常)")
        sys.exit(1)

    upsert_review_summary(lines, args.chain, args.why, args.review_num)
    upsert_scalar(lines, "revised", today)
    upsert_scalar(lines, "revision_note", revision_note)

    # ── 4. 写回 ──
    new_content = "".join(lines)
    with open(entity_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    rel = entity_path.relative_to(REPO)
    print(f"📄 {rel}")
    for c in changes:
        print(f"   ✓ {c}")

    # ── 5. 校验 ──
    print(f"\n🔍 validate.py ...")
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate.py")],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    # 始终打印 stdout
    if result.stdout.strip():
        print(result.stdout.strip())

    if result.returncode != 0:
        if result.stderr.strip():
            print(result.stderr.strip())
        print(f"❌ validate 失败 (exit {result.returncode})")
        sys.exit(1)

    print("✅ validate 通过")

    # ── 6. 可选:重生 INDEX ──
    if not args.no_index:
        print(f"\n📇 index.py ...")
        idx_result = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "index.py")],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        if idx_result.returncode != 0:
            print(idx_result.stderr.strip())
            print(f"⚠️  index 失败 (exit {idx_result.returncode}),但 validate 已通过")
        else:
            print("✅ INDEX.md 已重生")


if __name__ == "__main__":
    main()
