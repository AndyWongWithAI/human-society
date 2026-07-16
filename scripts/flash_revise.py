#!/usr/bin/env python3
"""flash_revise.py — 用 SenseNova 免费 deepseek-v4-flash 执行管线 revise。

绕过 Agent tool 的 LLM 费用：机械段(revise)不需要 pro 级推理，
用免费 flash 足够。Agent tool 只负责"运行本脚本+报告结果"——token 量极小。

用法:
    python scripts/flash_revise.py DED-031 \
        --fixes "1) 修正测量轴正交 2) 补全反例猎捕" \
        --review-round 2 \
        --review-path L3-deductions/reviews/ADV-REVIEW-038-DED-031.yaml

工作流:
    1. 读取实体 YAML + 审查档(本轮 required fixes 上下文)
    2. 构建 revise prompt 发到 SenseNova deepseek-v4-flash(免费)
    3. 用 flash 返回的完整内容覆写实体文件
    4. 更新 review_summary(追加本轮摘要)
    5. 跑 validate.py
    6. 输出 {done, validatorOk, note} 供 workflow agent 消费
"""

import sys
import os
import json
import subprocess
import argparse
from pathlib import Path
from datetime import date

REPO = Path(__file__).resolve().parent.parent

SENSENOVA_CONFIG_PATH = os.path.expanduser("~/.claude/secrets.json")


def load_sensenova_config():
    with open(SENSENOVA_CONFIG_PATH) as f:
        secrets = json.load(f)
    cfg = secrets.get("sensenova", {})
    return cfg["api_key"], cfg["base_url"], cfg.get("model", "deepseek-v4-flash")


def call_flash(api_key, base_url, model, system_prompt, user_prompt, max_tokens=8000):
    """调用 SenseNova deepseek-v4-flash。"""
    import requests

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,  # 机械修改，低温度
        },
        timeout=120,
    )
    if resp.status_code != 200:
        return None, f"API error {resp.status_code}: {resp.text[:500]}"
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return content, usage


def build_revise_prompt(entity_path, review_path, fixes, review_round):
    """构建 revise 提示词。"""
    entity_content = entity_path.read_text(encoding="utf-8")

    review_context = ""
    if review_path and review_path.exists():
        # 只取本轮 round 的内容
        review_text = review_path.read_text(encoding="utf-8")
        marker = f"round_{review_round}:"
        idx = review_text.find(marker)
        if idx > 0:
            # 取本轮到下一轮之间
            next_marker = f"round_{review_round + 1}:"
            next_idx = review_text.find(next_marker, idx + len(marker))
            if next_idx > 0:
                review_context = review_text[idx:next_idx]
            else:
                review_context = review_text[idx:]
        else:
            review_context = review_text[:3000]

    system = (
        "你是公理化推论的【整改者】。你的任务是对推论 YAML 文件做定向修改，"
        "严格按 required fixes 清单逐条修复，不碰清单之外的任何内容。\n\n"
        "规则:\n"
        "1. 只改 required fixes 涉及的段落，不动其他内容\n"
        "2. 保持 YAML 格式完整:多行文本用 | 块标量，中文冒号用\"：\"而非\": \"\n"
        "3. 缩进用 2 空格\n"
        "4. 每改完一处，确认该修复被真正消解\n"
        "5. 在 review_summary 字段末尾追加一行: \"r{round} needs_revision → (修复内容摘要)\"\n"
        "6. 输出【完整的修改后 YAML 文件内容】，不要输出解释或 diff，只输出完整 YAML"
    ).replace("{round}", str(review_round))

    user = (
        f"## Required Fixes (本轮必须修复)\n{fixes}\n\n"
        f"## 审查上下文 (round {review_round})\n{review_context[:3000]}\n\n"
        f"## 当前实体文件 (完整 YAML)\n```yaml\n{entity_content}\n```\n\n"
        "请输出修改后的完整 YAML 文件内容（不要解释，不要 diff，只要完整 YAML）:"
    )

    return system, user


def extract_yaml(response):
    """从 flash 响应中提取 YAML 内容。"""
    # 去掉可能的 markdown 代码块包装
    text = response.strip()
    if text.startswith("```yaml"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="用 SenseNova 免费 flash 执行管线 revise"
    )
    parser.add_argument("entity_id", help="实体 ID (如 DED-031)")
    parser.add_argument("--fixes", required=True, help="required fixes, 用 ; 分隔")
    parser.add_argument("--review-round", type=int, required=True, help="审查轮次")
    parser.add_argument("--review-path", default="", help="审查档路径(相对 repo 根)")
    parser.add_argument("--dry-run", action="store_true", help="只打印 prompt,不发 API")
    args = parser.parse_args()

    # ── 1. 查找实体 ──
    entity_path = None
    for d in ["L3-deductions/corollaries", "L4-composites",
              "L2-bridging/verified", "L2-bridging/weakly_verified", "L2-bridging/candidate"]:
        full = REPO / d
        if not full.exists():
            continue
        for f in sorted(full.glob(f"{args.entity_id}*.yaml")):
            content = f.read_text(encoding="utf-8")
            if f"id: {args.entity_id}" in content:
                entity_path = f
                break
        if entity_path:
            break

    if not entity_path:
        print(json.dumps({"done": False, "validatorOk": False,
                          "note": f"找不到实体 {args.entity_id}"}))
        sys.exit(1)

    review_path = REPO / args.review_path if args.review_path else None

    # ── 2. 构建 prompt ──
    system, user = build_revise_prompt(entity_path, review_path, args.fixes, args.review_round)

    if args.dry_run:
        print(f"📄 {entity_path.relative_to(REPO)}")
        print(f"   fixes: {args.fixes}")
        print(f"   system: {len(system)} chars, user: {len(user)} chars")
        print("   (dry-run, 未发 API)")
        return

    # ── 3. 调 SenseNova flash ──
    api_key, base_url, model = load_sensenova_config()
    print(f"🤖 调 SenseNova {model}...", file=sys.stderr)

    response, usage = call_flash(api_key, base_url, model, system, user)
    if response is None:
        print(json.dumps({"done": False, "validatorOk": False,
                          "note": f"API 调用失败: {usage}"}))
        sys.exit(1)

    tokens = usage.get("total_tokens", "?")
    print(f"   ✓ {tokens} tokens (免费)", file=sys.stderr)

    # ── 4. 提取 YAML 并写回 ──
    new_yaml = extract_yaml(response)

    # 安全检查:新内容必须有 id 和 status
    if "id:" not in new_yaml or "status:" not in new_yaml:
        print(json.dumps({"done": False, "validatorOk": False,
                          "note": "flash 输出不含 id/status,拒绝写入"}))
        sys.exit(1)

    # 备份 + 写入
    backup = entity_path.read_text(encoding="utf-8")
    entity_path.write_text(new_yaml, encoding="utf-8")

    # ── 5. 校验 ──
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate.py")],
        cwd=str(REPO), capture_output=True, text=True
    )
    if result.returncode != 0:
        # 校验失败，恢复备份
        entity_path.write_text(backup, encoding="utf-8")
        print(json.dumps({"done": False, "validatorOk": False,
                          "note": f"validate 失败,已恢复备份: {result.stderr[:300]}"}))
        sys.exit(1)

    print(json.dumps({"done": True, "validatorOk": True,
                      "note": f"flash revise ok, {tokens} tokens (free)"}))


if __name__ == "__main__":
    main()
