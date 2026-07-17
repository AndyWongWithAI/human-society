#!/usr/bin/env python3
"""author_draft.py — 免费模型起草推论初稿,供 pro Author agent 编辑(而非从零创作)。

动机: Author 段的认知动作是"读父推论→理解机制→合成新命题"。免费模型做不到
pro 的完整性(会漏 primary_suspect / 2×2 判空 / confidence 标注),但能出及格线以上
的骨架——pro 做编辑比做创作省 30-50% token。

用法:
    python scripts/author_draft.py --brief '{"id":"DED-050","slug":"...","title":"...",...}'
    python scripts/author_draft.py --brief-file /tmp/brief.json
    python scripts/author_draft.py --brief '...' --dry-run

输出(stdout,一行 JSON):
    {"done": true, "draftPath": "L3-deductions/corollaries/DED-050-slug.yaml", "validatorOk": true}

注意:
  - 实验性功能。草稿必有遗漏,pro Author agent 必须编辑后才能用。
  - 默认用 deepseek-v4-flash(最快免费模型)。调 zhipu 用 --provider zhipu(独立血统但慢)。
"""

import sys
import os
import json
import subprocess
import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS_PATH = os.path.expanduser("~/.claude/secrets.json")

PROVIDERS = {
    "sensenova": {"secret_key": "sensenova", "label": "SenseNova deepseek-v4-flash"},
    "zhipu": {"secret_key": "zhipu", "label": "智谱 glm-4-flash"},
}

# 精简版作者清单(挑最关键的发,不把完整 author-pack 塞进 prompt)
SLIM_CHECKLIST = """
## 必填项
- operationalization: 每个关键量(自变量/被预测量)写 definition + measurement(怎么测/分子/分母/切点) + limitations
- nontriviality_test: 2×2 排列表,每格判空(平凡/非平凡/反例/边界),至少一非平凡格
- falsification_trace.primary_suspect: 最脆弱环节(一句,定位到具体预测/因果链)
- falsification_trace.secondary_suspect(可选): 次脆弱环节
- real_world_anchors: supporting(≥1 条,含 anchor+evidence+confidence) + counterexamples(≥1 条,含 case+analysis+status)
- falsifiability: (a)(b)(c) 每条含测量口径+最小效应量,排除钩子必须物理可构造(BR-L2-025 判例)
- reverse_failure_modes: ≥1 条"命题在相反方向如何失败"(DED-039/047 判例)
- derivation.from_l2 + from_l3: 父推论引用
- 人话摘要: 一句非黑话解释

## statement 防不可证伪(BR-L2-025 教训)
- 区分定义性陈述(analytic)与经验预测(synthetic);核心因果声明必须是经验预测,不能藏在定义里
- 强主张("质变""独立维度""新玩家")降级为可证伪阈值主张("达阈值X时Y成为可能")
- 自变量测量轴必须与被预测量正交(DED-007 死因:不能只能通过社会效果反推)
- 阈值数字标来源(分布/先验/文献/历史基线),禁止无源魔术数字

## YAML 格式
- 多行叙述段用 | 块标量
- 缩进 2 空格
- 中文冒号用"：",ASCII 冒号后必须有空格
- status: candidate
"""


def load_provider(provider):
    with open(SECRETS_PATH) as f:
        secrets = json.load(f)
    key = PROVIDERS[provider]["secret_key"]
    cfg = secrets[key]
    return cfg["api_key"], cfg["base_url"], cfg["model"]


def call_free_model(api_key, base_url, model, system, user, max_tokens=12000):
    import requests
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.4,  # 略高温度,鼓励合成(pro 会修)
            "reasoning_effort": "none",  # 免费骨架,关思维链(措施3,去包裹层plan)
        },
        timeout=300,
    )
    if resp.status_code != 200:
        return None, f"API error {resp.status_code}: {resp.text[:500]}"
    data = resp.json()
    return data["choices"][0]["message"]["content"], data.get("usage", {})


def extract_yaml(text):
    text = text.strip()
    if text.startswith("```yaml"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="免费模型起草推论初稿(实验性),供 pro Author agent 编辑"
    )
    parser.add_argument("--brief", default="", help="brief JSON 字符串")
    parser.add_argument("--brief-file", default="", help="brief JSON 文件路径")
    parser.add_argument("--provider", default="sensenova", choices=["sensenova", "zhipu"],
                        help="免费模型 (default: sensenova,最快)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # 加载 brief
    if args.brief_file:
        with open(args.brief_file) as f:
            brief = json.load(f)
    elif args.brief:
        brief = json.loads(args.brief)
    else:
        print(json.dumps({"done": False, "note": "需要 --brief 或 --brief-file"}))
        sys.exit(1)

    entity_id = brief.get("id", "DED-???")
    slug = brief.get("slug", "untitled")
    layer = "L4-composites" if entity_id.startswith("L4-") else "L3-deductions"
    draft_path = REPO / layer / "corollaries" / f"{entity_id}-{slug}.yaml"

    # 构建 prompt
    system = (
        "你是公理化推论体系的【起草者】。你的任务是:根据 brief 写一份推论的候选 YAML 草稿。\n\n"
        "要求:\n"
        "1. 从父推论的机制出发,合成新的可证伪命题——不要只是复述父推论,要证明'1+1>2'\n"
        "2. 包含所有必填字段(见清单)\n"
        "3. statement 要清晰:核心机制+预测+推导步骤\n"
        "4. nontriviality_test 的 2×2 至少有一个非平凡格\n"
        "5. real_world_anchors 要有具体的 anchor(case+evidence+confidence)\n"
        "6. falsifiability 要具体可测,不是'可能有其他解释'的模糊护身符\n"
        "7. 防 BR-L2-025/DED-007 死因: 自变量测量轴必须与被预测量正交(不能只能通过社会效果反推); 强主张降级为可证伪阈值主张; 阈值数字标来源\n\n"
        "这是草稿——pro 模型还会编辑修正。优先完整性和可证伪性,措辞可粗糙。"
    )

    bricks_str = ", ".join(brief.get("bricks", brief.get("l3Parents", [])))
    domain_str = ", ".join(brief.get("domain", []))
    parent_info = ""
    if brief.get("bricks"):
        parent_info = f"承重砖(L2): {bricks_str}"
    elif brief.get("l3Parents"):
        parent_info = f"父推论(L3): {bricks_str}"
    if brief.get("l4Parents"):
        parent_info += f"\n父 L4: {', '.join(brief['l4Parents'])}"
    if brief.get("l2Parents"):
        parent_info += f"\nbridging: {', '.join(brief['l2Parents'])}"

    user = (
        f"## Brief\n"
        f"id: {entity_id}\n"
        f"title: {brief.get('title', '')}\n"
        f"coreClaim: {brief.get('coreClaim', brief.get('title', ''))}\n"
        f"domain: {domain_str}\n"
        f"{parent_info}\n\n"
        f"thesis:\n{brief.get('thesis', '')}\n\n"
        f"## 必填清单\n{SLIM_CHECKLIST}\n\n"
        f"## 输出\n"
        f"输出完整的 canonical YAML 文件内容(不要解释,不要 diff,只要 YAML)。\n"
        f"以 id: {entity_id} 开头。"
    )

    if args.dry_run:
        print(f"📄 draft → {draft_path.relative_to(REPO)}")
        print(f"🤖 provider: {PROVIDERS[args.provider]['label']}")
        print(f"   system: {len(system)} chars, user: {len(user)} chars")
        print("   (dry-run)")
        return

    api_key, base_url, model = load_provider(args.provider)
    label = PROVIDERS[args.provider]["label"]
    print(f"🤖 调 {label} 起草 {entity_id}...", file=sys.stderr)

    response, usage_or_error = call_free_model(api_key, base_url, model, system, user)
    if response is None:
        print(json.dumps({"done": False, "note": usage_or_error}))
        sys.exit(1)

    tokens = usage_or_error.get("total_tokens", "?")
    print(f"   ✓ {tokens} tokens (免费)", file=sys.stderr)

    new_yaml = extract_yaml(response)
    if f"id: {entity_id}" not in new_yaml:
        print(json.dumps({"done": False, "note": "草稿不含正确的 id,拒绝写入"}))
        sys.exit(1)

    # 确保 status: candidate
    if "status:" not in new_yaml:
        new_yaml = new_yaml.replace(f"id: {entity_id}", f"id: {entity_id}\nstatus: candidate")
    # 添加作者标注
    new_yaml += f"\nauthor: \"Claude via author_draft.py (free model draft, pending pro edit)\"\n"

    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(new_yaml, encoding="utf-8")

    # 跑 validate
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate.py")],
        cwd=str(REPO), capture_output=True, text=True
    )
    validator_ok = result.returncode == 0
    if not validator_ok:
        print(f"   ⚠️ validate 有警告(草稿正常): {result.stderr[:200]}", file=sys.stderr)

    print(json.dumps({
        "done": True,
        "draftPath": str(draft_path.relative_to(REPO)),
        "validatorOk": validator_ok,
        "note": f"free draft ok ({tokens} tokens), pending pro edit" + ("" if validator_ok else " — validate 有警告,pro 编辑时修正"),
    }))


if __name__ == "__main__":
    main()
