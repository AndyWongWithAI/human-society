#!/usr/bin/env python3
"""review_minimax.py - 用 MiniMax-M3 做独立对抗审查（异血统承重墙）。

Author 用 glm-5.2（智谱系），Review 用 MiniMax-M3（minimax 系）= 真正承重墙血统独立。
模式照 flash_revise.py：workflow agent 调本脚本，脚本调 minimax API（Anthropic 兼容）。

用法:
    python scripts/review_minimax.py DED-039 \\
        --review-round 1 \\
        --review-path L3-deductions/reviews/ADV-REVIEW-044-DED-039.yaml \\
        --layer L3

    # L4 推论（自动追加 l4-review-rubric.md 专属评分卡）
    python scripts/review_minimax.py L4-014 \\
        --review-round 1 \\
        --review-path L4-composites/reviews/ADV-REVIEW-L4-014.yaml \\
        --layer L4

工作流:
    1. 定位并读推论 YAML（审查对象全文）
    2. 读 reviewer-pack.md（评分卡16红旗+反例猎捕+裁决语义+实体速览）
       L4 时追加 l4-review-rubric.md（L4 专属红旗）
    3. 读前轮 review_summary（r2+ 时）
    4. 拼 Review prompt -> 调 MiniMax-M3（Anthropic 兼容）
    5. 解析分段输出 -> 手工拼 round_N 块 YAML（格式由脚本控制）
    6. 写审查档（追加 round_N 块或创建新档）
    7. 跑 validate.py
    8. 输出 JSON {done, validatorOk, verdict, requiredFixes[], counterexample, oneline}

血统独立性: MiniMax-M3 与 Author 的 glm-5.2 不同厂商=不同错误模式（ICV 协议）。
"""

import sys
import os
import json
import subprocess
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS_PATH = os.path.expanduser("~/.claude/secrets.json")
REVIEWER_PACK = REPO / "docs" / "pipeline" / "reviewer-pack.md"
L4_RUBRIC = REPO / "docs" / "pipeline" / "l4-review-rubric.md"


def load_minimax_config():
    """从 secrets.json 加载 minimax 配置。"""
    with open(SECRETS_PATH) as f:
        secrets = json.load(f)
    if "minimax" not in secrets:
        raise ValueError("secrets.json 中无 'minimax' 条目")
    cfg = secrets["minimax"]
    return cfg["api_key"], cfg["base_url"], cfg.get("model", "MiniMax-M3")


def call_minimax(api_key, base_url, model, system_prompt, user_prompt, max_tokens=12000, thinking=False, thinking_budget=4096):
    """调 MiniMax-M3（Anthropic 兼容格式）。thinking=True 启用思维链(措施4)。

    措施4 验证结论(2026-07-17): minimax thinking 接口支持(简短 prompt 正常),
    但对长 review prompt(reviewer-pack 74KB+推论全文)不实用--thinking 过度消耗,
    用满 max_tokens 致 text block 空输出(budget_tokens 不被严格遵守)。
    故默认 thinking=False。--thinking 仅短 prompt 场景可用。
    """
    import requests
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if thinking:
        # Anthropic thinking: max_tokens 须 > budget_tokens; budget 给思考, 剩余给输出
        body["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
    resp = requests.post(
        f"{base_url}/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=body,
        timeout=600,
    )
    if resp.status_code != 200:
        return None, f"API error {resp.status_code}: {resp.text[:500]}"
    data = resp.json()
    text_parts = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            text_parts.append(block.get("text", ""))
    content = "".join(text_parts)
    usage = data.get("usage", {})
    return content, usage


def locate_entity(entity_id):
    """glob 定位推论文件。"""
    patterns = [
        f"L3-deductions/corollaries/{entity_id}-*.yaml",
        f"L4-composites/corollaries/{entity_id}-*.yaml",
        f"L2-bridging/*/{entity_id}-*.yaml",
    ]
    for pat in patterns:
        matches = list(REPO.glob(pat))
        if matches:
            return matches[0]
    return None


def extract_review_summary(entity_path):
    """从推论 YAML 提取 review_summary 字段（r2+ 用）。"""
    try:
        import yaml
        with open(entity_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            return str(data.get("review_summary", "") or "")
    except Exception:
        pass
    return ""


def build_review_prompt(entity_path, entity_id, review_round, prev_summary, layer="L3"):
    """构建 Review prompt（system + user）。layer=L4 时追加 L4 专属评分卡。"""
    entity_text = entity_path.read_text(encoding="utf-8")
    pack_text = REVIEWER_PACK.read_text(encoding="utf-8") if REVIEWER_PACK.exists() else ""
    # L4 追加专属评分卡（L4 专属红旗，继承通用 16 条）
    extra_rubric = ""
    if layer == "L4" and L4_RUBRIC.exists():
        extra_rubric = "\n## L4 专属评分卡（追加红旗，继承通用 16 条；必须做多父逐格判空）\n" + \
                       L4_RUBRIC.read_text(encoding="utf-8")

    prev_section = ""
    if review_round > 1 and prev_summary:
        prev_section = f"""
## 前轮审查摘要（r1–r{review_round - 1}，读它即可，不读全量旧审查档）
{prev_summary}
"""

    system = (
        f"你是公理化体系的【独立对抗审查者】(round {review_round})，全新上下文，"
        f"与作者及前几轮审查者无关。你使用 MiniMax-M3，与作者使用的 glm-5.2 不同厂商--"
        f"这是血统级独立性（ICV 协议），你的价值在于'错得不一样'。"
        f"职责：尽最大努力打穿推论，给硬裁决。默认怀疑，宁可错杀不放水"
        f"（最高原则：方法论质量 > 任何单条推论）。"
    )

    user = f"""## 唯一校准来源（审查者阅读包，含实体速览+评分卡16红旗+反例猎捕+裁决语义）
{pack_text}
{extra_rubric}
{prev_section}
## 审查对象（推论全文）
{entity_text}

## 任务
按评分卡 16 条红旗逐条攻 + 反例猎捕（必做，判 verified 前必须留下反例猎捕过程）+ DED-004（不可证伪循环）/DED-007（测量轴焊死）复发检查。
{'L4 复合推论：额外必须做多父逐格判空归属分析（至少一个格子需≥2父推论合力，否则平凡合取），反例猎捕要猎"父推论都成立但交互不产生L4预测"。' if layer == 'L4' else ''}
裁决语义、verified 三条门全照评分卡。

## 输出格式（严格照此分段标记，每段都要有）
<<<VERDICT>>>
verified 或 needs_revision 或 rejected
<<<VERDICT_NOTE>>>
完整裁决说明：核心机制是否成立、焊接是否真实、反例猎捕结果、挡住 verified 的缺陷逐条。
<<<RED_FLAGS>>>
16 条红旗逐条：编号+命中/未命中/攻不穿，每条一到两句。
<<<COUNTEREXAMPLE_HUNT>>>
反例猎捕过程：构造了什么反例、结果（净杀/被消化/揭出过度伸张）。
<<<REQUIRED_FIXES>>>
无（若 verified）或 1) ... 2) ...（每条一行，≤5条，可操作）。
<<<ONELINE>>>
一句话总评。

严格独立。够格 verified 就明说；差一口气就精确指出差在哪。不制造假问题，也不放水。不要输出 markdown 代码块标记。"""
    return system, user


def parse_segments(raw):
    """解析 minimax 分段输出。"""
    import re
    labels = ["VERDICT", "VERDICT_NOTE", "RED_FLAGS",
              "COUNTEREXAMPLE_HUNT", "REQUIRED_FIXES", "ONELINE"]
    out = {}
    for lab in labels:
        pat = rf"<<<{lab}>>>\s*\n(.*?)(?=<<<\w+>>>|\Z)"
        m = re.search(pat, raw, re.DOTALL)
        out[lab] = m.group(1).strip() if m else ""
    return out


def _indent_block(text, prefix="    "):
    """块标量内容缩进（空行保持空）。"""
    return "\n".join(prefix + line if line.strip() else "" for line in text.split("\n"))


def _parse_fixes(fixes_raw):
    """REQUIRED_FIXES 文本拆成数组。"""
    lines = []
    if fixes_raw and fixes_raw != "无":
        for line in fixes_raw.split("\n"):
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def _clean_oneline(text):
    """清理 oneline 末尾 markdown 残留（``` 等）。"""
    t = text.strip()
    while t.endswith("```"):
        t = t[:-3].strip()
    return t


def write_review_block(review_path, review_round, seg, entity_id):
    """写审查档 round_N 块（追加或创建）。手工拼 YAML 保证格式。"""
    review_full = REPO / review_path
    review_full.parent.mkdir(parents=True, exist_ok=True)

    fixes_lines = _parse_fixes(seg.get("REQUIRED_FIXES", ""))

    block = f"\nround_{review_round}:\n"
    block += f"  reviewer: \"独立对抗审查者 MiniMax-M3 (round {review_round}, 异血统, 全新上下文, 与作者及前几轮审查者无关)\"\n"
    block += f"  verdict: {seg.get('VERDICT', 'needs_revision')}\n"
    block += f"  verdict_note: |\n{_indent_block(seg.get('VERDICT_NOTE', '(空)'))}\n"
    block += f"  red_flags: |\n{_indent_block(seg.get('RED_FLAGS', '(空)'))}\n"
    block += f"  counterexample_hunt: |\n{_indent_block(seg.get('COUNTEREXAMPLE_HUNT', '(空)'))}\n"
    if fixes_lines:
        block += "  required_fixes:\n"
        for fl in fixes_lines:
            fl_esc = fl.replace('"', '\\"')
            block += f'    - "{fl_esc}"\n'
    else:
        block += "  required_fixes: []\n"
    block += f"  oneline: |\n{_indent_block(_clean_oneline(seg.get('ONELINE', '(空)')))}\n"

    if review_full.exists():
        with open(review_full, "a", encoding="utf-8") as f:
            f.write(block)
    else:
        layer = ("L4-composites" if entity_id.startswith("L4-")
                 else "L3-deductions" if entity_id.startswith("DED-")
                 else "L2-bridging")
        header = f"""id: ADV-REVIEW-{entity_id}
type: adversarial_review
reviews: {entity_id}
layer: {layer}

人话摘要: |
  对 {entity_id} 的 round_{review_round} 独立对抗审查（MiniMax-M3 异血统）。

target: {entity_id}
protocol: |
  Rule B 独立对抗审查（作者≠审查者，MiniMax-M3 异血统独立上下文，ICV 协议）。
"""
        with open(review_full, "w", encoding="utf-8") as f:
            f.write(header + block)


def run_validate():
    """跑 validate.py。"""
    r = subprocess.run(
        ["python", "scripts/validate.py"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    return r.returncode == 0, (r.stdout[-400:] + r.stderr[-200:])


def main():
    parser = argparse.ArgumentParser(description="MiniMax-M3 异血统独立对抗审查")
    parser.add_argument("entity_id", help="推论 id (如 DED-039 / L4-014 / BR-L2-025)")
    parser.add_argument("--review-round", type=int, default=1, help="审查轮次")
    parser.add_argument("--review-path", required=True, help="审查档相对路径")
    parser.add_argument("--layer", default="L3", choices=["L3", "L4", "L2"],
                        help="推论层级（L4 追加专属评分卡）")
    parser.add_argument("--max-tokens", type=int, default=12000,
                        help="含 thinking budget + 输出")
    parser.add_argument("--thinking", action=argparse.BooleanOptionalAction, default=False,
                        help="启用 minimax thinking(措施4: 接口支持但长 review prompt 不实用--thinking 用满 max_tokens 致 text 空, default 关)")
    parser.add_argument("--thinking-budget", type=int, default=4096)
    args = parser.parse_args()

    entity_path = locate_entity(args.entity_id)
    if not entity_path:
        print(json.dumps({"done": False, "note": f"未找到推论 {args.entity_id}"}, ensure_ascii=False))
        return

    try:
        api_key, base_url, model = load_minimax_config()
    except Exception as e:
        print(json.dumps({"done": False, "note": f"配置加载失败: {e}"}, ensure_ascii=False))
        return

    prev_summary = extract_review_summary(entity_path) if args.review_round > 1 else ""
    system, user = build_review_prompt(entity_path, args.entity_id, args.review_round,
                                        prev_summary, args.layer)

    raw, usage = call_minimax(api_key, base_url, model, system, user, args.max_tokens,
                              thinking=args.thinking, thinking_budget=args.thinking_budget)
    if raw is None:
        print(json.dumps({"done": False, "note": f"minimax 调用失败: {usage}"}, ensure_ascii=False))
        return

    seg = parse_segments(raw)
    if not seg.get("VERDICT") or not seg.get("VERDICT_NOTE"):
        print(json.dumps({"done": False, "note": "minimax 输出解析失败（缺 VERDICT/VERDICT_NOTE）",
                          "raw_head": raw[:800]}, ensure_ascii=False))
        return

    write_review_block(args.review_path, args.review_round, seg, args.entity_id)
    validator_ok, validator_note = run_validate()

    result = {
        "done": True,
        "validatorOk": validator_ok,
        "verdict": seg.get("VERDICT", ""),
        "requiredFixes": _parse_fixes(seg.get("REQUIRED_FIXES", "")),
        "counterexample": seg.get("COUNTEREXAMPLE_HUNT", ""),
        "oneline": _clean_oneline(seg.get("ONELINE", "")),
        "model": model,
        "usage": usage,
        "note": "ok" if validator_ok else validator_note,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
