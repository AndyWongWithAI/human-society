#!/usr/bin/env python3
"""iea_survey.py — 免费模型做来源定性判断 + Python 做精确算术,替代 pro agent 的 IEA 段。

认知动作拆解:
  1. 免费模型(glm-4-flash / deepseek-v4-flash):读 applicable_sources → 逐来源判定 agree/disagree/mixed + 理由
  2. Python:查 independence-model → 应用成对独立系数 → 加权求和(算术不出错)
  3. Python:写入 cross_verification 段 + 仪器折扣披露
  4. Python:跑 validate.py

用法:
    python scripts/iea_survey.py BR-L2-029
    python scripts/iea_survey.py BR-L2-029 --provider zhipu
    python scripts/iea_survey.py BR-L2-029 --dry-run    # 只打印 prompt,不发 API

输出(stdout,一行 JSON):
    {"done": true, "ieaScore": 1.75, "sourceBreakdown": "锚 behav_econ 1.0 + cogn 0.25 + econ_hist 0.5 = 1.75", "validatorOk": true}
"""

import sys
import os
import json
import subprocess
import argparse
import re
from pathlib import Path
from datetime import date

REPO = Path(__file__).resolve().parent.parent
SECRETS_PATH = os.path.expanduser("~/.claude/secrets.json")

PROVIDERS = {
    "sensenova": {"secret_key": "sensenova", "label": "SenseNova deepseek-v4-flash"},
    "zhipu": {"secret_key": "zhipu", "label": "智谱 glm-4-flash"},
}

# ─── 工具函数 ───────────────────────────────────────────

def load_provider_config(provider):
    if provider not in PROVIDERS:
        raise ValueError(f"未知提供商: {provider}，可用: {list(PROVIDERS.keys())}")
    with open(SECRETS_PATH) as f:
        secrets = json.load(f)
    key = PROVIDERS[provider]["secret_key"]
    if key not in secrets:
        raise ValueError(f"secrets.json 中无 '{key}' 条目")
    cfg = secrets[key]
    return cfg["api_key"], cfg["base_url"], cfg.get("model", "glm-4-flash")


def call_free_model(api_key, base_url, model, system, user, max_tokens=3000):
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
            "temperature": 0.3,
        },
        timeout=180,
    )
    if resp.status_code != 200:
        return None, f"API error {resp.status_code}: {resp.text[:500]}", None
    data = resp.json()
    return data["choices"][0]["message"]["content"], None, data.get("usage", {})


def extract_json(text):
    """从免费模型响应中提取 JSON(可能包裹在 ```json 中)。"""
    text = text.strip()
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试提取 ```json 块
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    # 尝试提取第一个 { 到最后一个 }
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def find_bridge(entity_id):
    """在 L2-bridging 目录下定位桥接砖文件。"""
    for d in ["verified", "weakly_verified", "candidate"]:
        full = REPO / "L2-bridging" / d
        if not full.exists():
            continue
        for f in sorted(full.glob(f"{entity_id}*.yaml")):
            content = f.read_text(encoding="utf-8")
            if f"id: {entity_id}" in content:
                return f
    return None


def load_independence_model():
    """加载 independence-model,构建成对系数查找表。"""
    import yaml as _yaml
    model_path = REPO / "sources" / "independence-model.yaml"
    with open(model_path) as f:
        model = _yaml.safe_load(f)

    pairs = {}
    source_pairs = model.get("source_pairs", {})
    if isinstance(source_pairs, dict):
        for key, val in source_pairs.items():
            if not isinstance(val, dict) or "independence" not in val:
                continue
            coeff = val["independence"]
            parts = key.split("__")
            if len(parts) == 2:
                pairs[(parts[0], parts[1])] = coeff
                pairs[(parts[1], parts[0])] = coeff

    instrument = model.get("instrument_correlation", {})
    data_origin = model.get("data_source_origin", {})

    return {
        "default": model.get("default_independence", 0.6),
        "pairs": pairs,
        "discount_rule": instrument.get("discount_rule", ""),
        "data_origin": data_origin,
    }


def get_independence(source_a, source_b, indep_model):
    """查两来源间的独立系数,无记录用 default。"""
    coeff = indep_model["pairs"].get((source_a, source_b))
    if coeff is not None:
        return coeff
    return indep_model["default"]


def status_to_factor(status):
    """来源判定 → 权重因子。"""
    if status == "agree":
        return 1.0
    if status in ("partially_agree", "mixed"):
        return 0.5
    # disagree / mild_disagree → 不计权
    return 0.0


def compute_iea(votes, indep_model):
    """从逐票 [{source, status, note}] + independence-model 计算加权 IEA。

    算法:
      锚源(第一票,weight 1.0)为基准。
      其余每票: weight = independence(该源, 锚源) × status_factor
      IEA = sum(所有weight)
    """
    if not votes:
        return 0.0, {}, "无票"

    anchor = votes[0]["source"]
    total = 1.0  # 锚源
    weights = {anchor: 1.0}
    breakdown_parts = [f"{anchor} 1.0(锚源)"]

    for v in votes[1:]:
        src = v["source"]
        status = v.get("status", "mixed")
        coeff = get_independence(src, anchor, indep_model)
        factor = status_to_factor(status)
        w = round(coeff * factor, 2)
        weights[src] = w
        total += w
        breakdown_parts.append(f"{src} {w}(coeff={coeff}×{factor})")

    total = round(total, 2)
    breakdown = " + ".join(breakdown_parts) + f" = {total}"
    return total, weights, breakdown


def build_cross_verification_yaml(votes, iea_score, weights, indep_model, source_breakdown):
    """构建 cross_verification YAML 段(字符串)。"""
    today = date.today().isoformat()

    lines = ["cross_verification:", "  surveyed_by: IEA-survey (free-model + Python arithmetic)", f"  surveyed_date: {today}", "  votes:"]

    for v in votes:
        src = v["source"]
        status = v.get("status", "mixed")
        w = weights.get(src, 0.0)
        note = v.get("note", "").strip()
        # 多行 note 用 | 块标量
        lines.append(f"    {src}:")
        lines.append(f"      status: {status}")
        lines.append(f"      weight: {w}")
        lines.append(f"      evidence: []")
        if "\n" in note:
            lines.append(f"      note: |")
            for nl in note.split("\n"):
                lines.append(f"        {nl}")
        else:
            lines.append(f"      note: {note}")

    lines.append(f"  iea: {iea_score}")
    lines.append(f"  verdict_note: |")
    lines.append(f"    IEA = {source_breakdown}。")
    lines.append(f"    仪器折扣: 本次多路投票由单一免费 LLM 执行(来源判定)")
    lines.append(f"    + Python 脚本做算术(系数查表+加权求和)——报告 IEA 为学科独立性上限,")
    lines.append(f"    有效独立性低于此。独立人类专家或独立文献检索通道可部分恢复独立性。")

    return "\n".join(lines)


def build_prompt(bridge_path):
    """构建发给免费模型的提示词。"""
    bridge_text = bridge_path.read_text(encoding="utf-8")

    # 截取核心内容(statement + applicable_sources + falsifiability)
    # 避免过长导致免费模型超 context
    max_len = 12000
    if len(bridge_text) > max_len:
        # 保留前 max_len 字符(涵盖 id/status/term/statement/applicable_sources/falsifiability)
        bridge_text = bridge_text[:max_len] + "\n# ...(截断)"

    system = (
        "你是 L2 桥接砖的【来源判定员】。你的唯一任务是:对桥接砖的每个 applicable_source,"
        "独立判断该来源是否支持桥接砖的核心主张,给出 status 和详细理由。\n\n"
        "## 判定标准\n"
        "- agree: 来源的证据方向支持核心主张\n"
        "- partially_agree: 来源部分支持,但关键环节缺失或证据方向不完整\n"
        "- mixed: 来源同时包含支持和反对的证据\n"
        "- disagree: 来源的证据方向反对核心主张\n"
        "- mild_disagree: 来源的证据构成对核心主张的弱挑战\n\n"
        "## 关键原则\n"
        "1. 判断的是【该来源学科通道提供的证据类型和方向】是否支持核心主张,"
        "不是判断该学科本身是否正确\n"
        "2. **独立性意识**:锚源(第一个来源)以外的来源,要思考它是否真正独立于锚源——"
        "如果该来源的核心引证其实来自锚源学科(如认知科学通道引了行为经济学期刊的论文),"
        "应在 note 中指出'学科归属重叠,非真正独立通道'\n"
        "3. **方法论警示**:如果来源的证据类型与核心主张之间存在方法论文献的已知断层"
        "(如截面平均≠边际、实验室≠现场、人际≠制度),应在 note 中指出\n"
        "4. 锚源(第一个来源)通常 agree,但如果有反面证据也应诚实标注\n"
        "5. 每条 note 应包含:证据简述(引用 applicable_sources 中的具体研究/数据)+ 为何 agree/disagree + 独立性/方法论警示(如有)\n\n"
        "## 返回格式(纯 JSON,不要 markdown 包裹)\n"
        '{"votes": [{"source": "来源名", "status": "agree/partially_agree/mixed/disagree/mild_disagree", "note": "详细理由(含证据简述+判定理由+独立性/方法论警示)"}]}'
    )

    user = (
        f"## 桥接砖(含 statement + applicable_sources + falsifiability)\n"
        f"```yaml\n{bridge_text}\n```\n\n"
        "请逐来源判定。只返回 JSON。"
    )

    return system, user


def main():
    parser = argparse.ArgumentParser(
        description="IEA Survey — 免费模型定性判断 + Python 算术,替代 pro agent"
    )
    parser.add_argument("entity_id", help="桥接砖 ID (如 BR-L2-029)")
    parser.add_argument("--provider", default="zhipu", choices=["sensenova", "zhipu"],
                        help="免费模型提供商 (default: zhipu,独立血统)")
    parser.add_argument("--dry-run", action="store_true", help="只打印 prompt,不发 API")
    args = parser.parse_args()

    # ── 1. 定位桥接砖 ──
    bridge_path = find_bridge(args.entity_id)
    if not bridge_path:
        print(json.dumps({"done": False, "ieaScore": 0, "validatorOk": False,
                          "note": f"找不到桥接砖 {args.entity_id}"}))
        sys.exit(1)

    # ── 2. 加载 independence-model ──
    indep_model = load_independence_model()

    # ── 3. 构建 prompt + 调免费模型 ──
    system, user = build_prompt(bridge_path)

    if args.dry_run:
        label = PROVIDERS[args.provider]["label"]
        print(f"📄 {bridge_path.relative_to(REPO)}")
        print(f"🤖 provider: {label}")
        print(f"   system: {len(system)} chars, user: {len(user)} chars")
        print(f"   (dry-run, 未发 API)")
        return

    api_key, base_url, model = load_provider_config(args.provider)
    label = PROVIDERS[args.provider]["label"]
    print(f"🤖 调 {label} 做来源判定...", file=sys.stderr)

    response, error, usage = call_free_model(api_key, base_url, model, system, user)
    if error:
        print(json.dumps({"done": False, "ieaScore": 0, "validatorOk": False,
                          "note": error}))
        sys.exit(1)

    tokens = usage.get("total_tokens", "?")
    print(f"   ✓ {tokens} tokens (免费)", file=sys.stderr)

    # ── 4. 解析免费模型输出 ──
    result = extract_json(response)
    if not result:
        print(json.dumps({"done": False, "ieaScore": 0, "validatorOk": False,
                          "note": f"免费模型输出无法解析为 JSON: {response[:300]}"}))
        sys.exit(1)

    votes = result.get("votes", [])
    if not votes:
        print(json.dumps({"done": False, "ieaScore": 0, "validatorOk": False,
                          "note": "免费模型未返回 votes 数组"}))
        sys.exit(1)

    # ── 5. Python 做算术(精确) ──
    iea_score, weights, breakdown = compute_iea(votes, indep_model)
    print(f"   IEA = {breakdown}", file=sys.stderr)

    # ── 6. 构建 cross_verification YAML ──
    cv_yaml = build_cross_verification_yaml(votes, iea_score, weights, indep_model, breakdown)

    # ── 7. 写入桥接砖文件 ──
    full_text = bridge_path.read_text(encoding="utf-8")

    # 移除已有的 cross_verification 段(如果存在)
    if "\ncross_verification:" in full_text:
        idx = full_text.find("\ncross_verification:")
        # 找下一个顶级键(不缩进)或文件末尾
        rest = full_text[idx + 1:]  # 跳过 \n
        # 找下一个 \n 开头后紧跟非空格的字母+冒号
        next_section = re.search(r'\n(?!\s)([a-z_]+):', rest)
        if next_section:
            full_text = full_text[:idx] + "\n" + cv_yaml + "\n" + rest[next_section.start():]
        else:
            full_text = full_text[:idx] + "\n" + cv_yaml + "\n"
    else:
        # 追加到文件末尾
        full_text = full_text.rstrip() + "\n" + cv_yaml + "\n"

    # 备份 + 写入
    backup = bridge_path.read_text(encoding="utf-8")
    bridge_path.write_text(full_text, encoding="utf-8")

    # ── 8. 跑 validate.py ──
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate.py")],
        cwd=str(REPO), capture_output=True, text=True
    )
    if result.returncode != 0:
        # 校验失败,恢复备份
        bridge_path.write_text(backup, encoding="utf-8")
        print(json.dumps({"done": False, "ieaScore": iea_score, "validatorOk": False,
                          "note": f"validate 失败,已恢复备份: {result.stderr[:300]}"}))
        sys.exit(1)

    # ── 9. 输出结果(供 workflow agent 消费) ──
    print(json.dumps({
        "done": True,
        "ieaScore": iea_score,
        "sourceBreakdown": breakdown,
        "validatorOk": True,
    }))


if __name__ == "__main__":
    main()
