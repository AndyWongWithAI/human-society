# 数据模型与前端输出 · 现状盘点

> **性质**：只读盘点，不动代码。作为后续重构方案的基线。
> 范围：`scripts/export_graph.py`（导出）→ `visualization/graph-data.{js,json}`（存储）→ `visualization/index.html`（前端消费）/ `api.py`（API 暴露）。
> 分支：`task/data-model-refactor`。盘点日期：2026-07-17。

**一句话结论**：前端为了配合后端数据模型，背了一整套自己用不上的设施--最重的是整套无人调用的 API 层，其次是四处冗余的文章数据、双份导出产物、三处重复的颜色/标签定义。

---

## 数据流总览

```
YAML 实体(L0-L4) ──> export_graph.py ──┬─> graph-data.js    (706KB, window.GRAPH_DATA)
                                       └─> graph-data.json  (706KB, 同内容)
                                                ├─> 前端 index.html  (fetch JSON, 不调 API)
                                                └─> api.py ─> /api/*  (7 端点, 内部零消费)
articles.yaml ─> export_articles ─> articles.js (window.ARTICLE_DATA)
                 └─同内容嵌入─> graph-data.{js,json}  └─> api.py 也返回 articles
```

### 节点字段（export_graph.py:281-294 产出）

`id`, `term`, `term_zh`, `type`, `layer`, `layer_label`, `status`, `人话摘要`, `statement`, `domain`, `created`, `revised`, `depends_on_count`, `depended_by_count`

### 边字段（export_graph.py:314-321 产出）

`source`, `target`, `relation`, `relation_label`
relation 四种：`depends_on` / `bridges_to` / `derived_from` / `grounded_in`（`derivation.from_l1/l2/l3` 与 `l0_constraints` 都归并进 `depends_on` / `grounded_in`）。

---

## 前端为配合后端做的多余工作

### 🔴 严重（架构错位）

**A. API 层整套是死代码。**
- 前端 `loadData()`（index.html:325-352）只 `fetch('/graph-data.json')`，**不调任何 `/api/*`**（grep `"/api/` 在 index.html 零命中）。
- `api.py`(62 行) + systemd 服务 `human-society-api` + nginx 反代 `/api/* -> 127.0.0.1:8090` + index.html 的 API 文档弹窗(743-776 行) -- 全套服务于零个内部消费者。
- API 弹窗还给用户展示一套前端自己都没用过的接口文档。

**B. 文章"安全边界"已失效，文档与实现矛盾。**
- CLAUDE.md 声称："`/api/nodes/{id}` 和 `/graph-data.json` 均不含文章数据"。
- 实际：
  - `graph-data.json` 含 `entity_articles`（export_graph.py:352-354 把它写入 output，JSON 与 JS 同源同内容，grep `entity_articles` 在 graph-data.json 命中）。
  - `api.py:35` 返回 `articles = data.get("entity_articles", {}).get(node_id, [])`。
- 文章数据实际**四处冗余**：graph-data.js / graph-data.json / articles.js / API。

### 🟡 中（冗余存储 + 重复定义）

**C. graph-data.js 与 graph-data.json 内容完全重复（706KB×2）。**
- 前端主路径 fetch JSON，graph-data.js 仅作 catch 回退（index.html:331-335）。
- 同源同服务器，JSON fetch 失败时 JS 全局变量也大概率加载不到，回退路径基本不可达。

**D. 颜色/标签三处定义，且不一致。**
- CSS `.type-colors` 块（index.html:31-39）：**死代码**，定义的 `--c-*` 变量全文件无引用（grep `var(--c-` 零命中）。
- JS `TYPE_COLORS` / `TYPE_LABELS`（index.html:355-372）：前端自维护。
- 节点 `layer_label` 字段：后端导出但**前端不用**（grep `layer_label` 在 index.html 零命中），前端另维护 `LAYER_LABELS`（index.html:374）。
- **两份不一致**：后端 L1="定义层"/L2="桥接层"/L3="推论层"/L4="复合推论层"；前端 L1="定义"/L2="桥接"/L3="推论"/L4="复合"。

**E. 节点冗余字段。**
- `depends_on_count` / `depended_by_count`（export_graph.py:334-335 计算）：前端不用，自己用 `upstreamMap[id].length` / `downstreamMap[id].length` 现算（grep 在 index.html 零命中）。
- `meta.layers` / `meta.types`（export_graph.py:340-345）：前端只用 `meta.generated_at`（index.html:422），layers/types 自己现算（`buildLayerTabs` 的 counts）。

**F. articles 双通道。**
- graph-data.json 已嵌 `entity_articles`，articles.js 又是一份相同内容。
- 前端先读 `data.entity_articles`，空了才回退 `window.ARTICLE_DATA.entity_articles`（index.html:348-351）。

### 🟢 轻（小瑕疵）

**G. `term_en` 丢失。** `split_term`（export_graph.py:163-171, 265）已解析出英文（如 "Agent"）但**未写入节点**。前端想显示英文只能回退显示整串 "行动者 (Agent)"（index.html:598 用 `n.term`）。

**H. `term_zh || n.term` fallback 重复 4 处**（index.html:515/598/673 等）。若后端保证 term_zh 非空可消除。

**I. relation 四种区分对前端无意义。** 前端只用 `relation_label` 显示文字（index.html:675 `${arrow} ${e.relation}`），不区分 depends_on/bridges_to/derived_from/grounded_in 语义。导出端维护 4 种提取 + 标签映射，消费端只取中文标签。

---

## 重构方向（初步，未动代码）

| # | 动作 | 收益 | 风险 |
|---|---|---|---|
| 1 | **API 去留二选一**。短期无外部消费者 → 砍 api.py + systemd + nginx 反代 + API 弹窗，前端只读静态 JSON。要保留对外能力 → 前端改用 API、砍 JSON 回退与 graph-data.js。当前"前端读 JSON、API 也读 JSON"双轨是纯浪费 | 砍一整个服务，或消除双轨 | 需先确认 API 是否有外部/未来消费者 |
| 2 | **文章数据定一处**。要么只进 graph-data.json（承认边界已破、改 CLAUDE.md），要么只进 articles.js（恢复边界、从 JSON/API 摘除） | 四份 → 一份 | 影响部署路径触发条件 |
| 3 | **颜色/标签单一来源**。删 CSS 死代码 + 删节点 `layer_label` 字段，前端单一 JS 配置（或后端导出 `type_label`/`type_color`） | 消除三处重复 + 不一致 | 低 |
| 4 | **删冗余字段** `depends_on_count`/`depended_by_count`/`meta.layers`/`meta.types` | 缩小 graph-data | 低，前端已不依赖 |
| 5 | **补 `term_en` 导出**（split_term 已解析，写进节点） | 消除 4 处 fallback + 修复英文显示 | 低 |
| 6 | **graph-data.js 与 graph-data.json 二选一**。保留 JSON（API/前端共用），删 JS 全局变量回退 | 706KB×2 → ×1 | 低，回退路径基本不可达 |

---

## 验证依据（grep 命中行号，均可复现）

| 判断 | 命令 | 结果 |
|---|---|---|
| CSS `.type-colors` 死代码 | `grep -n 'type-colors\|var(--c-' index.html` | 仅 31 行定义，无引用 |
| 冗余 count 字段 | `grep -n 'depends_on_count\|depended_by_count' index.html` | 零命中 |
| 前端不调 API | `grep -n '"/api/\|fetch.*api' index.html` | 零命中 |
| 前端不用 layer_label | `grep -n 'layer_label' index.html` | 零命中 |
| 文章进 JSON | `grep -c 'entity_articles' graph-data.json` | 命中 |
| meta.layers/types 不用 | `grep -n 'meta.*layers\|meta.*types' index.html` | 零命中 |
| term_en 未导出 | `grep -n 'term_en' export_graph.py` | 仅 265 行解析，无写入 |
| term fallback 重复 | `grep -c 'term_zh \|\| n.term' index.html` | 4 处 |

---

## 下一步

本盘点是基线。后续重构方案需对上面 6 条逐一定决策（尤其 #1 API 去留、#2 文章边界方向），再产出文件级改动清单。
