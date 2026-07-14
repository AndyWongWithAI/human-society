#!/usr/bin/env python3
"""index.py — 实体紧凑索引生成器

从所有实体 YAML 抽 id / status / term / 摘要 / 承重依赖,生成定长紧凑 INDEX.md。
目的:未来 agent 先读这一份索引(~1 行/条)了解"有什么、各说了啥",
只在真需核对时才开某几份全文——把碰存量实体的读取成本【封顶】,不随实体增多滚雪球。

实体发现逻辑与 validate.py 一致(同一批实体)。索引可随时重生,绝不过时:
    cd <repo> && python scripts/index.py
"""
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"iterations", ".git", "__pycache__", "docs"}
OUT = ROOT / "INDEX.md"

# 分组:(路径片段, 组标题) —— 顺序即输出顺序
GROUPS = [
    ("L0-physical", "L0 物理约束"),
    ("L1-definitions/concepts", "L1 · 概念 concepts"),
    ("L1-definitions/axioms", "L1 · 公理 axioms"),
    ("L1-definitions/theorems", "L1 · 定理 theorems"),
    ("L1-definitions/contested", "L1 · 争议 contested"),
    ("L2-bridging", "L2 桥接 bridges"),
    ("L3-deductions/corollaries", "L3 推论 corollaries"),
    ("L3-deductions/reviews", "L3 审查 reviews"),
    ("L3-deductions", "L3 其它(经验检验/交叉验证等)"),
]

SUMMARY_MAX = 72  # 摘要截断字符数


def load():
    es = {}
    for f in ROOT.rglob("*.yaml"):
        if any(d in f.parts for d in SKIP):
            continue
        if f.name in ("independence-model.yaml", "META.yaml"):
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                d = yaml.safe_load(fh)
            if d and isinstance(d, dict) and "id" in d:
                es[str(f.relative_to(ROOT))] = d
        except yaml.YAMLError:
            pass  # 交给 validate.py 报;索引只跳过
    return es


def summary(e):
    """一行摘要:优先人话摘要,退而 statement / term。"""
    for key in ("人话摘要", "statement", "term"):
        v = e.get(key)
        if not v:
            continue
        s = str(v).strip().strip('"').strip("'").strip()
        # 取首句/首行
        for sep in ("。", "\n", ";", ";"):
            if sep in s:
                s = s.split(sep)[0]
                break
        s = s.strip().strip('"').strip("'").replace("\n", " ")
        if len(s) > SUMMARY_MAX:
            s = s[:SUMMARY_MAX] + "…"
        return s
    return ""


def deps(e):
    """承重依赖(承重砖/定理/公理/父推论/L0),跳过概念以保持紧凑。"""
    out = []
    for container in ("depends_on", "bridges_to"):
        c = e.get(container)
        if isinstance(c, dict):
            for k in ("l0_constraints", "axioms", "theorems", "bridging", "deductions"):
                out += [str(x) for x in (c.get(k) or []) if isinstance(x, str)]
        elif isinstance(c, list):
            out += [str(x) for x in c if isinstance(x, str) and x[:1].isupper()]
    # 去重保序
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def line(e):
    eid = e.get("id", "?")
    st = e.get("status") or e.get("verdict") or ""
    st = f" [{st}]" if st else ""
    term = e.get("term") or ""
    # term 去掉英文括号部分保持短
    term = str(term).split("(")[0].strip().strip('"')
    head = f"{eid}{st}"
    if term:
        head += f" · {term}"
    s = summary(e)
    d = deps(e)
    tail = f"  ⟵ {', '.join(d)}" if d else ""
    body = f" — {s}" if s and s != term else ""
    return f"- {head}{body}{tail}"


def group_of(path):
    for frag, title in GROUPS:
        if frag in path:
            return title
    return "其它"


def main():
    es = load()
    # 按组归类
    buckets = {title: [] for _, title in GROUPS}
    buckets.setdefault("其它", [])
    for path, e in es.items():
        buckets.setdefault(group_of(path), []).append((e.get("id", ""), e))
    total = len(es)

    lines = [
        "# INDEX.md — 实体紧凑索引",
        "",
        "> 自动生成,**勿手改**。实体增删改后跑 `python scripts/index.py` 重生。",
        "> 用途:未来 agent【先读本索引】了解已有实体与依赖,只在需核对时才开某几份全文——",
        "> 把碰存量实体的读取成本封顶,不随实体增多滚雪球。",
        "> 行格式:`id [status] · term — 摘要  ⟵ 承重依赖`",
        "",
        f"**{total} 实体**",
        "",
    ]
    for _, title in GROUPS:
        items = buckets.get(title, [])
        if not items:
            continue
        items.sort(key=lambda t: t[0])
        lines.append(f"## {title} ({len(items)})")
        for _, e in items:
            lines.append(line(e))
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ INDEX.md 已生成:{total} 实体 → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
