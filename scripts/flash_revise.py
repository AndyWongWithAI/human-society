#!/usr/bin/env python3
"""flash_revise.py - 用免费 flash 模型执行管线 revise（双厂商）。

绕过 Agent tool 的 LLM 费用：机械段(revise)不需要 pro 级推理，
用免费 flash 足够。Agent tool 只负责"运行本脚本+报告结果"--token 量极小。

两种模式:
  --mode overwrite (默认, 旧行为): flash 输出完整 YAML 覆写文件。
      风险: flash 可能在重排/重写时丢失字段或改了不该改的字段。
  --mode patch (C2, 2026-07-16): flash 只输出要改的字段的完整新内容(带路径),
      Python 按路径定位整块替换, 并强校验"未改字段原样"。
      收益: 输出 token ↓60-80%; 覆写风险 ↓(flash 物理上碰不到未改字段)。

用法:
    # 默认 SenseNova (deepseek-v4-flash), overwrite 模式
    python scripts/flash_revise.py DED-031 \
        --fixes "1) 修正测量轴正交 2) 补全反例猎捕" \
        --review-round 2 \
        --review-path L3-deductions/reviews/ADV-REVIEW-038-DED-031.yaml

    # C2 patch 模式 (字段级覆写)
    python scripts/flash_revise.py DED-031 \
        --mode patch --cross-check \
        --fixes "..." --review-round 2 --review-path ...

    # 智谱 (glm-4-flash, 独立血统)
    python scripts/flash_revise.py DED-031 --provider zhipu --fixes "..."

提供商:
    sensenova (默认) - deepseek-v4-flash, 1M上下文, 1.3s
    zhipu              - glm-4-flash, 独立血统(非DeepSeek系), 2.6s

工作流:
    1. 读取实体 YAML + 审查档(本轮 required fixes 上下文)
    2. 构建 revise prompt 发到指定提供商的免费 flash 模型
    3. overwrite: flash 返回完整 YAML 覆写文件
       patch: flash 返回字段级 patch, Python 应用 + 校验未改字段原样
    4. 更新 review_summary(追加本轮摘要)
    5. 跑 validate.py
    6. 输出 {done, validatorOk, note, ...} 供 workflow agent 消费
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

# 提供商注册表
PROVIDERS = {
    "sensenova": {
        "secret_key": "sensenova",
        "label": "SenseNova deepseek-v4-flash",
    },
    "zhipu": {
        "secret_key": "zhipu",
        "label": "智谱 glm-4-flash",
    },
}


def load_provider_config(provider="sensenova"):
    """从 secrets.json 加载指定提供商的 API 配置。"""
    if provider not in PROVIDERS:
        raise ValueError(f"未知提供商: {provider}，可用: {list(PROVIDERS.keys())}")
    with open(SENSENOVA_CONFIG_PATH) as f:
        secrets = json.load(f)
    secret_key = PROVIDERS[provider]["secret_key"]
    if secret_key not in secrets:
        raise ValueError(f"secrets.json 中无 '{secret_key}' 条目，请先配置")
    cfg = secrets[secret_key]
    return cfg["api_key"], cfg["base_url"], cfg.get("model", "glm-4-flash")


def call_flash(api_key, base_url, model, system_prompt, user_prompt, max_tokens=12000):
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
            "reasoning_effort": "none",  # 机械段关思维链(措施3,去包裹层plan)
        },
        timeout=300,
    )
    if resp.status_code != 200:
        return None, f"API error {resp.status_code}: {resp.text[:500]}"
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return content, usage


# ============ prompt 构建 ============

def _load_review_context(review_path, review_round):
    """从审查档取本轮 round 的上下文。"""
    if not review_path or not review_path.exists():
        return ""
    review_text = review_path.read_text(encoding="utf-8")
    marker = f"round_{review_round}:"
    idx = review_text.find(marker)
    if idx > 0:
        next_marker = f"round_{review_round + 1}:"
        next_idx = review_text.find(next_marker, idx + len(marker))
        if next_idx > 0:
            return review_text[idx:next_idx]
        return review_text[idx:]
    return review_text[:3000]


def build_overwrite_prompt(entity_path, review_path, fixes, review_round):
    """构建 overwrite 模式 prompt(旧行为): 要求 flash 输出完整 YAML。"""
    entity_content = entity_path.read_text(encoding="utf-8")
    review_context = _load_review_context(review_path, review_round)

    system = (
        "你是公理化推论的【整改者】。你的任务是对推论 YAML 文件做定向修改，"
        "严格按 required fixes 清单逐条修复，不碰清单之外的任何内容。\n\n"
        "规则:\n"
        "1. 只改 required fixes 涉及的段落，不动其他内容\n"
        "2. 保持 YAML 格式完整:多行文本用 | 块标量，中文冒号用\"：\"而非\": \"\n"
        "3. 缩进用 2 空格\n"
        "4. 每改完一处，确认该修复被真正消解\n"
        "5. 在 review_summary 字段末尾追加一行: \"r{round} needs_revision -> (修复内容摘要)\"\n"
        "6. 输出【完整的修改后 YAML 文件内容】，不要输出解释或 diff，只输出完整 YAML"
    ).replace("{round}", str(review_round))

    user = (
        f"## Required Fixes (本轮必须修复)\n{fixes}\n\n"
        f"## 审查上下文 (round {review_round})\n{review_context[:3000]}\n\n"
        f"## 当前实体文件 (完整 YAML)\n```yaml\n{entity_content}\n```\n\n"
        "请输出修改后的完整 YAML 文件内容（不要解释，不要 diff，只要完整 YAML）:"
    )

    return system, user


def build_patch_prompt(entity_path, review_path, fixes, review_round):
    """构建 patch 模式 prompt(C2): 要求 flash 只输出要改的字段(带路径)。

    flash 输出字段级 patch, Python 按路径定位整块替换。flash 物理上碰不到
    未在 patch 中声明的字段 -> 覆写风险从"靠 flash 自觉"降到"结构强制"。
    """
    entity_content = entity_path.read_text(encoding="utf-8")
    review_context = _load_review_context(review_path, review_round)

    system = (
        "你是公理化推论的【整改者】。严格按 required fixes 清单逐条修复。\n\n"
        "【输出格式 - 字段级 patch, 禁止输出完整文件】\n"
        "对每一个需要修改的字段, 输出一个 patch 块:\n\n"
        "<<<PATCH>>>\n"
        "path: <字段路径, 点分定位嵌套字段, 例如 operationalization.activity_measurability.limitations>\n"
        "body: |\n"
        "  <该字段的完整新内容, YAML 格式, 从字段名开始, 缩进从 0 开始。例如:>\n"
        "  limitations: |\n"
        "    三维度编码(在看任何行业边界数据前锁定):\n"
        "    ...(完整新内容)...\n"
        "<<<END>>>\n\n"
        "可以输出多个 <<<PATCH>>> 块, 每个对应一个要改的字段。\n\n"
        "规则:\n"
        "1. 只输出需要修改的字段, 不要输出未改的字段(这是 patch 模式的核心, 省 token + 防误改)\n"
        "2. path 用点分路径定位嵌套字段(如 derivation.steps / review_summary / "
        "falsification_trace.primary_suspect)。顶层字段就是字段名本身(如 review_summary)\n"
        "3. body 是该字段【完整的新内容】, YAML 格式, 第一行是字段名(缩进 0), 多行值用 | 块标量\n"
        "4. body 内缩进用 2 空格, 与原文保持一致\n"
        "5. review_summary 字段: 在原内容末尾追加一行 \"r{round} needs_revision -> (修复摘要)\" 后整体输出\n"
        "6. 不要输出解释、不要输出完整文件、不要输出未改字段\n"
        "7. 一个 fix 可能需要改多个字段 -> 输出多个 patch 块"
    ).replace("{round}", str(review_round))

    user = (
        f"## Required Fixes (本轮必须修复)\n{fixes}\n\n"
        f"## 审查上下文 (round {review_round})\n{review_context[:3000]}\n\n"
        f"## 当前实体文件 (完整 YAML, 供你判断要改哪些字段)\n```yaml\n{entity_content}\n```\n\n"
        "请输出字段级 patch(<<<PATCH>>> 块)。只输出要改的字段, 不要输出完整文件:"
    )

    return system, user


def build_revise_prompt(entity_path, review_path, fixes, review_round, mode="overwrite"):
    """构建 revise 提示词(按 mode 分流)。"""
    if mode == "patch":
        return build_patch_prompt(entity_path, review_path, fixes, review_round)
    return build_overwrite_prompt(entity_path, review_path, fixes, review_round)


# ============ overwrite 模式: YAML 提取 ============

def extract_yaml(response):
    """从 flash 响应中提取 YAML 内容。"""
    text = response.strip()
    if text.startswith("```yaml"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ============ patch 模式: 解析 + 定位 + 应用 + 校验 ============

PATCH_START = "<<<PATCH>>>"
PATCH_END = "<<<END>>>"


def parse_patches(raw):
    """解析 flash 输出的字段级 patch 块。

    返回 [{field, body}, ...]。解析失败返回空列表。
    格式:
        <<<PATCH>>>
        path: some.field.path
        body: |
          fieldname: |
            content...
        <<<END>>>
    """
    patches = []
    i = 0
    text = raw
    while True:
        s = text.find(PATCH_START, i)
        if s < 0:
            break
        e = text.find(PATCH_END, s)
        if e < 0:
            break
        block = text[s + len(PATCH_START):e].strip()
        # 解析 path 和 body
        path = None
        body = None
        lines = block.split("\n")
        j = 0
        while j < len(lines):
            line = lines[j]
            if line.startswith("path:"):
                path = line[len("path:"):].strip()
            elif line.startswith("body:"):
                # body 是 | 块标量, 后续缩进行是内容
                rest = line[len("body:"):].strip()
                body_lines = []
                if rest == "|" or rest == "":
                    # 收集后续缩进行
                    k = j + 1
                    # 确定 body 内容的基准缩进
                    base_indent = None
                    while k < len(lines):
                        bl = lines[k]
                        if bl.strip() == "":
                            body_lines.append(bl)
                            k += 1
                            continue
                        cur_indent = len(bl) - len(bl.lstrip())
                        if base_indent is None:
                            base_indent = cur_indent
                        if cur_indent < base_indent and bl.strip():
                            break
                        # 去掉一层缩进
                        body_lines.append(bl[base_indent:] if len(bl) >= base_indent else bl)
                        k += 1
                    body = "\n".join(body_lines).rstrip()
                    j = k
                    continue
                else:
                    body = rest
            j += 1
        if path and body is not None:
            patches.append({"field": path, "body": body})
        i = e + len(PATCH_END)
    return patches


def locate_field_block(lines, field_path):
    """定位嵌套字段块的行范围 [start, end)。

    field_path: 点分路径如 'operationalization.activity_measurability.limitations'。
    返回 (start_idx, end_idx) 或 None。start 是字段所在行, end 是下一同级字段行(不含)。
    块标量内容行(缩进更深)被包含在 [start, end) 内。
    """
    parts = field_path.split(".")
    search_from = 0
    parent_indent = -1  # 根级: 任何 indent >= 0 都在搜索范围
    found_line = -1
    for depth, part in enumerate(parts):
        expected_indent = depth * 2
        found = False
        i = search_from
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                i += 1
                continue
            this_indent = len(line) - len(stripped)
            # 出了当前父块(缩进回退到父级或更上) -> 没找到
            if depth > 0 and this_indent <= parent_indent:
                return None
            if this_indent == expected_indent:
                key = stripped.split(":", 1)[0].strip().lstrip("-").strip()
                if key == part:
                    found_line = i
                    search_from = i + 1
                    parent_indent = expected_indent
                    found = True
                    break
            i += 1
        if not found:
            return None
    start = found_line
    field_indent = len(lines[start]) - len(lines[start].lstrip())
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        this_indent = len(line) - len(stripped)
        if this_indent <= field_indent:
            end = j
            break
    return (start, end)


def split_top_fields(text):
    """把 YAML 按顶层字段分块。返回 {field_name: block_text}(保序用 list 更稳, 这里够用)。"""
    lines = text.split("\n")
    blocks = {}
    current_name = None
    current_lines = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            if current_name:
                current_lines.append(line)
            continue
        indent = len(line) - len(stripped)
        if indent == 0:
            if current_name:
                blocks[current_name] = "\n".join(current_lines)
            key = stripped.split(":", 1)[0].strip()
            current_name = key
            current_lines = [line]
        else:
            if current_name:
                current_lines.append(line)
    if current_name:
        blocks[current_name] = "\n".join(current_lines)
    return blocks


def insert_top_field(lines, body):
    """新建顶层字段,插入到 depends_on/domain/created 前(与 finalize upsert 一致)。"""
    body_lines = body.rstrip("\n").split("\n")
    insert_at = len(lines)
    for i, line in enumerate(lines):
        if line.startswith(("depends_on:", "domain:", "created:",
                            "revised:", "revision_note:")):
            insert_at = i
            break
    body_lines.insert(0, "")  # 前空行
    lines[insert_at:insert_at] = body_lines


def apply_patches(original_text, patches):
    """把字段级 patch 应用到原文(支持替换已有字段 + 新建顶层字段)。

    返回 (new_text, applied_fields, failed_fields)。
    顺序应用,每次重新定位(避免行号偏移)。嵌套字段新建不支持(报失败)。
    """
    text = original_text
    applied = []
    failed = []
    for p in patches:
        lines = text.split("\n")
        loc = locate_field_block(lines, p["field"])
        if loc is not None:
            # 替换已有字段
            start, end = loc
            indent = len(lines[start]) - len(lines[start].lstrip())
            indent_str = " " * indent
            body_lines = p["body"].rstrip("\n").split("\n")
            adjusted = [indent_str + bl if bl else "" for bl in body_lines]
            lines[start:end] = adjusted
            text = "\n".join(lines)
            applied.append(p["field"])
        else:
            # 新建(仅顶层字段;嵌套字段新建不支持)
            parts = p["field"].split(".")
            if len(parts) == 1:
                insert_top_field(lines, p["body"])
                text = "\n".join(lines)
                applied.append(p["field"])
            else:
                failed.append(p["field"])
    return text, applied, failed


def verify_untouched(original, patched, patch_fields):
    """校验未在 patch_fields 中的顶层字段是否原样。

    返回 (ok, changed_fields)。patch 涉及的顶层字段(取 path 第一段)允许变, 其余必须原样。
    这堵住 flash 在 patch 模式下偷偷改其他字段的口子(虽然它本就碰不到, 但应用器
    若定位错也可能波及 -- 此校验兜底)。
    """
    patch_tops = {f.split(".")[0] for f in patch_fields}
    orig_blocks = split_top_fields(original)
    patch_blocks = split_top_fields(patched)
    changed = []
    for name, block in orig_blocks.items():
        if name in patch_tops:
            continue
        if name not in patch_blocks:
            changed.append(f"{name}(缺失)")
        elif block.rstrip() != patch_blocks[name].rstrip():
            changed.append(name)
    for name in patch_blocks:
        if name not in orig_blocks and name not in patch_tops:
            changed.append(f"{name}(新增)")
    return (len(changed) == 0, changed)


# ============ 单次 revise ============

def run_single_revise(provider, system_prompt, user_prompt, entity_path, mode="overwrite"):
    """单次 revise: 调指定提供商的免费模型, 产出修改后文本, 跑 validate。

    返回 (new_text, ok, note, extra)。不写文件, 由调用方决定是否写入。
    extra: overwrite={}; patch={patchFields, failedFields, untouchedOk, untouchedChanged}
    """
    api_key, base_url, model = load_provider_config(provider)
    label = PROVIDERS[provider]["label"]
    print(f"🤖 调 {label} (mode={mode})...", file=sys.stderr)

    response, usage = call_flash(api_key, base_url, model, system_prompt, user_prompt)
    if response is None:
        return None, False, f"{provider} API 调用失败: {usage}", {}

    tokens = usage.get("total_tokens", "?")
    out_tokens = usage.get("completion_tokens", "?")
    print(f"   ✓ {provider}: {tokens} tokens (免费, 输出 {out_tokens})", file=sys.stderr)

    backup = entity_path.read_text(encoding="utf-8")
    extra = {}

    if mode == "patch":
        patches = parse_patches(response)
        if not patches:
            return None, False, f"{provider} patch 解析失败(无有效 <<<PATCH>>> 块)", {}
        new_text, applied, failed = apply_patches(backup, patches)
        if failed:
            return (None, False,
                    f"{provider} patch 字段定位失败: {failed}", {})
        if not applied:
            return None, False, f"{provider} patch 无可应用字段", {}
        untouched_ok, untouched_changed = verify_untouched(backup, new_text, applied)
        extra = {
            "patchFields": applied,
            "failedFields": failed,
            "untouchedOk": untouched_ok,
            "untouchedChanged": untouched_changed[:10],
            "outTokens": out_tokens,
        }
        if not untouched_ok:
            return (None, False,
                    f"{provider} 未改字段被改动(应用器或 flash 出错): {untouched_changed[:5]}",
                    extra)
        new_yaml = new_text
    else:
        new_yaml = extract_yaml(response)
        if "id:" not in new_yaml or "status:" not in new_yaml:
            return None, False, f"{provider} 输出不含 id/status", {}
        extra = {"outTokens": out_tokens}

    # 临时写入并校验(不覆盖原文件)
    entity_path.write_text(new_yaml, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate.py")],
        cwd=str(REPO), capture_output=True, text=True
    )
    if result.returncode != 0:
        entity_path.write_text(backup, encoding="utf-8")
        return None, False, f"{provider} validate 失败: {result.stderr[:200]}", extra

    # 校验通过, 恢复备份(由调用方决定写入)
    entity_path.write_text(backup, encoding="utf-8")
    note = f"{provider} revise ok, {tokens} tokens (free, mode={mode})"
    return new_yaml, True, note, extra


def _normalize(text):
    """规范化 YAML 文本用于比较:统一换行、去尾部空格。"""
    return "\n".join(line.rstrip() for line in text.split("\n"))


def _validate_or_rollback(entity_path, backup):
    """跑 validate.py, 失败则回滚。返回 (ok, err)。"""
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate.py")],
        cwd=str(REPO), capture_output=True, text=True
    )
    if result.returncode != 0:
        entity_path.write_text(backup, encoding="utf-8")
        return False, result.stderr[:300]
    return True, ""


def main():
    parser = argparse.ArgumentParser(
        description="用免费 flash 模型执行管线 revise（双厂商，支持交叉验证 + 字段级 patch）"
    )
    parser.add_argument("entity_id", help="实体 ID (如 DED-031)")
    parser.add_argument("--provider", default="sensenova", choices=["sensenova", "zhipu"],
                        help="免费模型提供商 (default: sensenova)")
    parser.add_argument("--fixes", required=True, help="required fixes, 用 ; 分隔")
    parser.add_argument("--review-round", type=int, required=True, help="审查轮次")
    parser.add_argument("--review-path", default="", help="审查档路径(相对 repo 根)")
    parser.add_argument("--mode", default="overwrite", choices=["overwrite", "patch"],
                        help="overwrite=全文覆写(旧); patch=字段级覆写(C2, 省 token+防误改)")
    parser.add_argument("--dry-run", action="store_true", help="只打印 prompt,不发 API")
    parser.add_argument("--cross-check", action="store_true",
                        help="双厂商交叉验证:两家都跑,diff 对比,一致=高置信")
    args = parser.parse_args()

    # ── 1. 查找实体 ──
    entity_path = None
    for d in ["L3-deductions/corollaries", "L4-composites/corollaries",
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

    # ── 2. 构建 prompt(双厂商共享同一 prompt) ──
    system, user = build_revise_prompt(entity_path, review_path, args.fixes,
                                       args.review_round, mode=args.mode)

    if args.dry_run:
        print(f"📄 {entity_path.relative_to(REPO)}  (mode={args.mode})")
        print(f"   fixes: {args.fixes}")
        print(f"   system: {len(system)} chars, user: {len(user)} chars")
        if args.cross_check:
            print(f"   mode: cross-check (sensenova + zhipu)")
        print("   (dry-run, 未发 API)")
        return

    backup = entity_path.read_text(encoding="utf-8")

    if args.cross_check:
        # ── 双厂商交叉验证 ──
        providers_to_run = ["sensenova", "zhipu"]
        results = {}
        for prov in providers_to_run:
            txt, ok, note, extra = run_single_revise(prov, system, user, entity_path, mode=args.mode)
            results[prov] = {"text": txt, "ok": ok, "note": note, "extra": extra}

        ok_count = sum(1 for r in results.values() if r["ok"])
        if ok_count == 0:
            print(json.dumps({"done": False, "validatorOk": False,
                              "note": f"双厂商均失败: { {k:v['note'] for k,v in results.items()} }"}))
            sys.exit(1)

        # 对比应用后结果(两种模式都是对比最终文本)
        if ok_count == 2:
            ya = results["sensenova"]["text"]
            yb = results["zhipu"]["text"]
            if _normalize(ya) == _normalize(yb):
                entity_path.write_text(ya, encoding="utf-8")
                diff_note = "双厂商一致(deepseek-v4-flash ≡ glm-4-flash),高置信"
            else:
                entity_path.write_text(ya, encoding="utf-8")
                diff_lines = sum(1 for a, b in zip(_normalize(ya).split("\n"),
                                                   _normalize(yb).split("\n")) if a != b)
                diff_lines += abs(len(_normalize(ya).split("\n")) - len(_normalize(yb).split("\n")))
                diff_note = f"双厂商差异({diff_lines} 行不同),保留 sensenova,需人工扫一眼"
            print(f"   cross-check: {diff_note}", file=sys.stderr)
        else:
            winner = "sensenova" if results["sensenova"]["ok"] else "zhipu"
            loser = "zhipu" if winner == "sensenova" else "sensenova"
            entity_path.write_text(results[winner]["text"], encoding="utf-8")
            diff_note = f"仅 {winner} 通过,{loser} 失败: {results[loser]['note']}"
            print(f"   cross-check: {diff_note}", file=sys.stderr)

        ok, err = _validate_or_rollback(entity_path, backup)
        if not ok:
            print(json.dumps({"done": False, "validatorOk": False,
                              "note": f"cross-check 写入后 validate 失败: {err}"}))
            sys.exit(1)

        # 汇总 extra(取主厂商)
        win = "sensenova" if results["sensenova"]["ok"] else "zhipu"
        out = {"done": True, "validatorOk": True,
               "note": f"cross-check revise ok - {diff_note}"}
        out.update(results[win]["extra"])
        print(json.dumps(out))
        return

    # ── 单厂商模式 ──
    txt, ok, note, extra = run_single_revise(args.provider, system, user, entity_path, mode=args.mode)
    if not ok:
        print(json.dumps({"done": False, "validatorOk": False, "note": note}))
        sys.exit(1)

    entity_path.write_text(txt, encoding="utf-8")
    ok, err = _validate_or_rollback(entity_path, backup)
    if not ok:
        print(json.dumps({"done": False, "validatorOk": False,
                          "note": f"validate 失败,已恢复备份: {err}"}))
        sys.exit(1)

    out = {"done": True, "validatorOk": True, "note": note}
    out.update(extra)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
