#!/usr/bin/env python3
"""author_pro.py - glm-5.2 Python 直调 Author(去包裹层 plan 措施1)。

动机: ded_pipeline.workflow.js / l4_pipeline.workflow.js 的 Author 段外包一层
glm-5.2 workflow agent, 该 agent 的编排循环(读文件/思考/写文件/跑 validate)是
108 倍成本根因(见 docs/plans/2026-07-17-pipeline-debanding-plan.md)。本脚本把
Author 段 Python 化: 经 SenseNova 网关直调 glm-5.2(reasoning_effort=high), 省掉
workflow agent 包裹层。freeDraft 骨架(author_draft.py)可作输入, 本脚本编辑成稿。

接入(仿 blind_coder.py): secrets.json["sensenova"] 的 base_url + api_key,
model="glm-5.2"(智谱系, 与 Review 的 minimax 异血统)。reasoning_effort="high"--
Author 是创作, 是唯一需要思维链的付费阶段。

用法:
    # 从零创作(L3)
    python scripts/author_pro.py --brief-file /tmp/brief-DED-055.json --layer L3

    # 编辑 freeDraft 骨稿(L4)
    python scripts/author_pro.py --brief-file /tmp/brief.json --layer L4 \\
        --draft L4-composites/corollaries/L4-020-xxx.yaml

    # 不调 API, 只看 prompt 规模
    python scripts/author_pro.py --brief-file /tmp/brief.json --layer L3 --dry-run

输出(stdout, 一行 JSON):
    {"done": true, "draftPath": "L3-deductions/corollaries/DED-055-slug.yaml",
     "validatorOk": true, "model": "glm-5.2", "note": "ok"}

YAML 严格前置门(吸收 human-society-model-swap-verdict 教训: validate.py 静默吞错):
写文件前 yaml.safe_load 自检 + id 校验, 失败则把错误回灌模型重试(最多 3 次)。
避免 glm-5.2 格式失败被 validate 宽容路径放行导致质量 silently 下降。
"""

import sys
import os
import json
import subprocess
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS_PATH = os.path.expanduser("~/.claude/secrets.json")
AUTHOR_PACK = REPO / "docs" / "pipeline" / "author-pack.md"
L4_CHECKLIST = REPO / "docs" / "pipeline" / "l4-author-checklist.md"

GLM_MODEL = "glm-5.2"
MAX_TOKENS = 16000  # 完整 canonical YAML 需要较大输出


def load_sensenova():
    """从 secrets.json 加载 SenseNova 网关配置(glm-5.2 经此网关调, 仿 blind_coder.py)。"""
    with open(SECRETS_PATH) as f:
        secrets = json.load(f)
    if "sensenova" not in secrets:
        raise ValueError("secrets.json 中无 'sensenova' 条目")
    cfg = secrets["sensenova"]
    return cfg["api_key"], cfg["base_url"]


def call_glm(api_key, base_url, system, user, max_tokens=MAX_TOKENS, reasoning_effort="high"):
    """调 glm-5.2(SenseNova 网关, OpenAI 兼容)。reasoning_effort=high 开思维链。"""
    import requests
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": GLM_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,  # 格式严格, 低温度
            "reasoning_effort": reasoning_effort,  # Author 创作需要思维链
        },
        timeout=600,
    )
    if resp.status_code != 200:
        return None, f"API error {resp.status_code}: {resp.text[:500]}"
    data = resp.json()
    return data["choices"][0]["message"]["content"], data.get("usage", {})


def extract_yaml(text):
    """剥离 ```yaml 围栏。"""
    text = text.strip()
    if text.startswith("```yaml"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def validate_yaml_strict(text, entity_id):
    """YAML 严格前置门: safe_load + 顶层 mapping + id 校验。

    返回 (ok, msg)。这是 model-swap-verdict 教训的防线: validate.py 用 try/except
    吞 YAMLError, 坏文件静默跳过; 本前置门在写文件前主动自检, 失败即重试, 不依赖
    validate 的宽容路径。
    """
    import yaml
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return False, f"YAML 解析失败: {e}"
    if not isinstance(data, dict):
        return False, f"顶层非 mapping(实际 {type(data).__name__})"
    if data.get("id") != entity_id:
        return False, f"id 不匹配: 期望 {entity_id}, 实际 {data.get('id')}"
    return True, "ok"


def build_prompt(brief, layer, draft_text=None):
    """构建 Author prompt(system + user)。读 author-pack 全文(与 workflow Author agent 对等)。"""
    pack_text = AUTHOR_PACK.read_text(encoding="utf-8") if AUTHOR_PACK.exists() else ""
    extra_checklist = ""
    if layer == "L4" and L4_CHECKLIST.exists():
        extra_checklist = "\n## L4 专属前置清单(逐条自查规则 E/F/G + L4 专属字段格式)\n" + \
                          L4_CHECKLIST.read_text(encoding="utf-8")

    draft_section = ""
    if draft_text:
        draft_section = (
            "\n## ⚠️ 免费模型草稿(已存在)\n"
            "你的任务从'从零起草'变为'读草稿->修正遗漏->补全必填项->产出合格 YAML'。"
            "草稿必有遗漏(primary_suspect/2×2判空/confidence标注/L4专属字段), 重点检查这些。\n\n"
            f"```yaml\n{draft_text}\n```"
        )

    entity_id = brief.get("id", "DED-???")
    domain_str = ", ".join(brief.get("domain", []))
    parent_info = ""
    if brief.get("bricks"):
        parent_info = f"承重砖(L2): {', '.join(brief['bricks'])}"
    elif brief.get("l3Parents"):
        parent_info = f"父推论(L3): {', '.join(brief['l3Parents'])}"
    if brief.get("l4Parents"):
        parent_info += f"\n父 L4: {', '.join(brief['l4Parents'])}"

    system = (
        "你是公理化推论体系【作者】, 全新上下文。"
        "目标: 把给定推论写成一份【瘦身 canonical】的 candidate YAML。\n\n"
        "要求:\n"
        "1. 从父推论的机制出发, 合成新的可证伪命题--不要只复述父推论, 要证明'1+1>2'\n"
        "2. 包含所有必填字段(见阅读包前置清单 A-E 段): nontriviality_test / falsification_trace"
        "(primary_suspect) / real_world_anchors / falsifiability / reverse_failure_modes\n"
        "3. statement 要清晰: 核心机制+预测+推导步骤\n"
        "4. nontriviality_test 的 2×2 至少一个非平凡格\n"
        "5. real_world_anchors: supporting(≥1) + counterexamples(≥1), 含 case+evidence+confidence\n"
        "6. falsifiability 具体可测, 非'可能有其他解释'的模糊护身符\n"
        "7. 防 BR-L2-025/DED-007 死因: 自变量测量轴与被预测量正交(不能只通过社会效果反推); "
        "强主张降级为可证伪阈值主张; 阈值数字标来源\n"
        "8. YAML 格式严格: 多行叙述段用 | 块标量; 裸标量禁 ASCII 冒号+空格; status: candidate\n"
        "9. reverse_failure_modes 必填且非空(DED-039/047 判例, C1 后新增): ≥1 条"
        "'命题在相反方向如何失败'的描述(列表, 每条一段)。缺此字段视为不合格, 必须产出\n\n"
        "你使用 glm-5.2, 带思维链(reasoning_effort=high), 这是创作任务, 请深度推理后输出。\n"
        "只输出完整 canonical YAML(不要解释/不要 diff), 以 `id: <entity_id>` 开头。"
    )

    user = f"""## 作者阅读包(实体速览+前置清单+瘦身 canonical 格式, 读完这份通用部分全覆盖)
{pack_text}
{extra_checklist}
{draft_section}

## 要写的推论
- id: {entity_id}   layer: {layer}
- 主题: {brief.get('title', '')}
- 核心一句话: {brief.get('coreClaim', brief.get('title', ''))}
- domain: {domain_str}
{parent_info}
- 论点/承重逻辑/招牌预测:
{brief.get('thesis', '')}

## 输出
输出完整的 canonical YAML 文件内容(不要解释, 不要 diff, 只要 YAML)。
以 `id: {entity_id}` 开头。"""
    return system, user


def run_validate():
    """跑 validate.py。"""
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate.py")],
        cwd=str(REPO), capture_output=True, text=True,
    )
    return r.returncode == 0, (r.stdout[-400:] + r.stderr[-200:])


def main():
    ap = argparse.ArgumentParser(description="glm-5.2 Python 直调 Author(去包裹层 plan 措施1)")
    ap.add_argument("--brief", default="", help="brief JSON 字符串")
    ap.add_argument("--brief-file", default="", help="brief JSON 文件路径")
    ap.add_argument("--layer", required=True, choices=["L3", "L4"],
                    help="推论层级(L4 追加专属清单)")
    ap.add_argument("--draft", default="", help="freeDraft 骨架文件相对路径(编辑模式)")
    ap.add_argument("--reasoning-effort", default="high",
                    help="思维链强度(default: high, Author 创作需要)")
    ap.add_argument("--dry-run", action="store_true", help="不调 API, 只看 prompt 规模")
    args = ap.parse_args()

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
    layer_dir = "L4-composites" if layer_is_l4(args.layer) else "L3-deductions"
    out_path = REPO / layer_dir / "corollaries" / f"{entity_id}-{slug}.yaml"

    # 读 freeDraft 骨架(若有)
    draft_text = None
    if args.draft:
        draft_full = REPO / args.draft
        if draft_full.exists():
            draft_text = draft_full.read_text(encoding="utf-8")
        else:
            print(json.dumps({"done": False, "note": f"草稿不存在: {args.draft}"}))
            sys.exit(1)

    system, user = build_prompt(brief, args.layer, draft_text)

    if args.dry_run:
        print(f"📄 author_pro -> {out_path.relative_to(REPO)}")
        print(f"🤖 model: {GLM_MODEL} (reasoning_effort={args.reasoning_effort})")
        print(f"   system: {len(system)} chars, user: {len(user)} chars")
        print("   (dry-run)")
        return

    try:
        api_key, base_url = load_sensenova()
    except Exception as e:
        print(json.dumps({"done": False, "note": f"配置加载失败: {e}"}))
        sys.exit(1)

    print(f"🤖 调 {GLM_MODEL} (reasoning_effort={args.reasoning_effort}) 起草 {entity_id}...",
          file=sys.stderr)

    # ── YAML 严格前置门 + 失败回灌重试(最多 3 次) ──
    yaml_text = None
    last_err = ""
    total_usage = {}
    for attempt in range(1, 4):
        if attempt > 1:
            user_try = user + (
                f"\n\n## ⚠️ 上次输出 YAML 解析失败(第{attempt - 1}次)\n"
                f"错误: {last_err}\n"
                "请修正后重新输出完整 YAML(只输出 YAML, 以 `id: " + entity_id + "` 开头)。"
            )
        else:
            user_try = user
        response, usage = call_glm(api_key, base_url, system, user_try,
                                   reasoning_effort=args.reasoning_effort)
        if response is None:
            last_err = usage  # 失败时 usage 字段存错误信息
            print(f"   ⚠️ 第{attempt}次 API 失败: {last_err[:80]}", file=sys.stderr)
            continue
        if isinstance(usage, dict):
            total_usage = usage
        candidate = extract_yaml(response)
        ok, msg = validate_yaml_strict(candidate, entity_id)
        if ok:
            yaml_text = candidate
            print(f"   ✓ 第{attempt}次 YAML 通过前置门 "
                  f"({total_usage.get('total_tokens', '?')} tokens)", file=sys.stderr)
            break
        last_err = msg
        print(f"   ⚠️ 第{attempt}次 YAML 前置门失败: {msg[:80]}", file=sys.stderr)

    if yaml_text is None:
        print(json.dumps({"done": False, "model": GLM_MODEL,
                          "note": f"YAML 3次未通过前置门: {last_err[:200]}"}))
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml_text, encoding="utf-8")

    validator_ok, validator_note = run_validate()
    if not validator_ok:
        print(f"   ⚠️ validate 未过: {validator_note[:200]}", file=sys.stderr)

    print(json.dumps({
        "done": True,
        "draftPath": str(out_path.relative_to(REPO)),
        "validatorOk": validator_ok,
        "model": GLM_MODEL,
        "reasoning_effort": args.reasoning_effort,
        "attempts": attempt,
        "usage": total_usage,
        "note": "ok" if validator_ok else f"validate 未过: {validator_note[:120]}",
    }, ensure_ascii=False))


def layer_is_l4(layer):
    return layer == "L4"


if __name__ == "__main__":
    main()
