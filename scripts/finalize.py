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
    "L4-composites/corollaries",
    "L2-bridging/verified",
    "L2-bridging/weakly_verified",
    "L2-bridging/candidate",
]

VALID_TRANSITIONS = {
    "candidate": ["verified", "verified*", "weakly_verified", "rejected"],
    "weakly_verified": ["verified", "rejected", "candidate"],
    "verified": ["candidate"],   # 降级:前提 rejected 连带,verified 地位失效
    # weakly_verified 是 L2 标准状态,L2 管线可从 candidate 直翻 weakly_verified(IEA < 1.8)
    # verified/weakly -> candidate: 前提 rejected 连带降级(非审查裁决,跳过 Q2)
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
    """写入/覆写一个简单标量字段。自动引用含 ': ' 的值以免 YAML 解析错误。"""
    # 若值含 ASCII 冒号+空格,引用以免被 YAML 当做嵌套 mapping
    if ": " in value:
        value = f'"{value}"'
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


# ============ Q2: 反例猎捕硬门(2026-07-16) ============
# 翻 verified 前校验审查档该轮 counterexample_hunt 非空,堵"敷衍型 verified"
# (审查者没认真做反例猎捕就判 verified)。空/敷衍 -> 拒绝翻牌,退回审查。
# 审查干预只朝严方向(红线),故只在 verified/verified* 时校验,rejected 不校验。

HUNT_MIN_LEN = 20  # 去空白后最少字符数(历史合法最短~26,挡纯空/敷衍词)


def find_review_doc(entity_id: str, review_num: str, last_round: str) -> Path | None:
    """定位审查档(兼容 L3/L4/L2 三种命名 + 多轮分档)。

    L3: ADV-REVIEW-{num}-DED-{id}.yaml
    L4: ADV-REVIEW-L4-{num}-L4-{id}.yaml
    L2: ADV-REVIEW-{id}.yaml(无编号)
    分档: ADV-REVIEW-{num}-{id}-round{N}.yaml
    """
    candidates = []
    for d in ["L3-deductions/reviews", "L4-composites/reviews", "L2-bridging/reviews"]:
        full = REPO / d
        if not full.exists():
            continue
        for f in full.glob(f"ADV-REVIEW-*{entity_id}*.yaml"):
            candidates.append(f)
    if not candidates:
        return None
    # 优先1:档名含 round{last_round}(分档命名)
    for f in candidates:
        if f"round{last_round}" in f.name or f"round_{last_round}" in f.name:
            return f
    # 优先2:档名含 review_num
    if review_num:
        for f in candidates:
            if review_num in f.name and "round" not in f.name:
                return f
    # 兜底:不含 round 的单档(多 round 都在档内)
    for f in candidates:
        if "round" not in f.name:
            return f
    return candidates[0]


def check_counterexample_hunt(entity_id: str, review_num: str, chain: str) -> tuple[bool, str]:
    """Q2: 校验审查档该轮 counterexample_hunt 非空。

    返回 (ok, msg)。空/缺失/过短 -> (False, 原因),拒绝翻牌。
    """
    rounds = re.findall(r"r(\d+)", chain)
    if not rounds:
        return False, f"无法从 chain 解析轮次: {chain}"
    last_round = rounds[-1]

    review_path = find_review_doc(entity_id, review_num, last_round)
    if not review_path:
        return False, f"找不到审查档(entity={entity_id}, review_num={review_num})"

    txt = review_path.read_text(encoding="utf-8")
    # 优先:在 round_{last_round}: 块内找
    marker = f"round_{last_round}:"
    idx = txt.find(marker)
    if idx >= 0:
        next_idx = txt.find("\nround_", idx + len(marker))
        block = txt[idx:next_idx] if next_idx > 0 else txt[idx:]
    else:
        # 分档命名(档内只一轮)或无 round 标记 -> 全档
        block = txt

    m = re.search(r"counterexample_hunt:\s*\|?\s*\n((?:[ \t]+.*\n)*)", block)
    if not m:
        return False, (
            f"{review_path.name} round_{last_round} 无 counterexample_hunt 字段"
            f"(反例猎捕硬门未过)"
        )
    content = m.group(1)
    nonws = re.sub(r"\s", "", content)
    if len(nonws) < HUNT_MIN_LEN:
        return False, (
            f"counterexample_hunt 过短({len(nonws)}字符<{HUNT_MIN_LEN},"
            f"疑似敷衍未做反例猎捕)"
        )
    return True, f"round_{last_round} counterexample_hunt ok({len(nonws)}字符)"


def main():
    parser = argparse.ArgumentParser(
        description="翻牌最终化:status 翻转 + review_summary 压缩 + validate"
    )
    parser.add_argument("id", help="实体 ID (如 DED-031, BR-L2-025, L4-005)")
    parser.add_argument(
        "--verdict",
        required=True,
        choices=["verified", "verified*", "rejected", "candidate"],
        help="目标定论",
    )
    parser.add_argument(
        "--chain",
        default="",
        help='审查裁决链 (如 "r1 needs_revision -> r2 verified")',
    )
    parser.add_argument("--why", required=True, help="一句话:为何是这个定论")
    parser.add_argument(
        "--review-num", default="", help="ADV-REVIEW 编号 (如 038);降级可省"
    )
    parser.add_argument("--note", default="", help="可选 revision_note(默认自动生成)")
    parser.add_argument(
        "--target-status",
        default="",
        help="覆盖目标 status(用于 L2 IEA 判定:verified vs weakly_verified)",
    )
    parser.add_argument(
        "--move-to",
        default="",
        help="目标子目录(如 L2-bridging/weakly_verified/),相对 repo 根;finalize 后用 git mv 移动文件",
    )
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
    backup_content = "".join(lines)  # validate 失败时回滚
    old_status = detect_status(lines)
    if old_status is None:
        print(f"❌ 找不到 status 字段")
        sys.exit(1)

    # 降级(candidate)不需要 chain/review-num;翻牌需要
    if args.verdict == "candidate":
        args.chain = args.chain or "降级(前提rejected连带,非审查裁决)"
        args.review_num = args.review_num or "N/A"
    elif not args.chain or not args.review_num:
        print("❌ 翻牌需要 --chain 和 --review-num(降级 --verdict candidate 除外)")
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

    # ── Q2: 反例猎捕硬门(仅 verified/verified*,不朝松方向) ──
    if args.verdict in ("verified", "verified*"):
        hunt_ok, hunt_msg = check_counterexample_hunt(args.id, args.review_num, args.chain)
        if not hunt_ok:
            print(f"❌ 反例猎捕硬门未过: {hunt_msg}")
            print("   不翻牌,退回审查(审查干预只朝严方向,符合红线)")
            sys.exit(1)
        print(f"🛡  反例猎捕硬门: {hunt_msg}")

    target_status = args.target_status or args.verdict
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
        entity_path.write_text(backup_content, encoding="utf-8")  # 回滚
        if result.stderr.strip():
            print(result.stderr.strip())
        print(f"❌ validate 失败 (exit {result.returncode}),已回滚备份")
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

    # ── 7. 可选:移动文件 ──
    if args.move_to:
        target_dir = REPO / args.move_to
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / entity_path.name

        # 如果目标已存在同名文件(不应发生,但防御)
        if target_path.exists() and target_path != entity_path:
            print(f"⚠️  目标已存在 {target_path.relative_to(REPO)},跳过移动")
        elif target_path != entity_path:
            result = subprocess.run(
                ["git", "mv", str(entity_path), str(target_path)],
                cwd=str(REPO),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"⚠️  git mv 失败: {result.stderr.strip()}")
                # fallback: regular mv
                import shutil
                shutil.move(str(entity_path), str(target_path))
                print(f"   → 已用 mv 回退")
            else:
                print(f"📦 已移至 {target_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
