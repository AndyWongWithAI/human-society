# 数据模型与前端重构 · 改动方案

> **性质**：文件级改动清单，待执行。基于 `2026-07-17-data-model-frontend-audit.md` 盘点 + 第一性原理审查修正。
> 分支：`task/data-model-refactor`。日期：2026-07-17。
> **状态**：3 处明确修正已落地；2 处权衡（#1 API 性价比 / #2 articles 归属）待用户拍板（见"待决策项"）。

## 第一性分层（审查确立的标尺）

- **数据层**（graph-data.json）：原始事实--id / type / layer / status / 关系。面向所有消费者，**不含任何呈现文案**。
- **展示层**（index.html）：中文标签、颜色、截断、布局。只给人看。
- **服务层**（api.py）：对外的查询能力。

凡"给人看的呈现"不得进数据层；凡"数据固有的属性"可进数据层。

## 决策汇总

| # | 盘点结论 | 最终决策 | 审查修正 |
|---|---|---|---|
| 1 | API 层死代码 | **待决策**（见待决策项） | 补"性价比权衡"告知，用户知情后定 |
| 2 | 文章四处冗余 | **待决策**（见待决策项） | 补"关注点分离"代价，列中间项 |
| 3 | 颜色/标签三处重复 | 删 CSS 死代码；`TYPE_COLORS`/`TYPE_LABELS` **保留**（展示层）；`layer_label` **分层使用**（tab 短标签 + 详情用 node.layer_label） | **撤回 type_label 新增**（展示泄漏数据层）；**改 layer_label 一刀切为分层**（护 UI） |
| 4 | 冗余字段 | 基本不动 | API 保留后 meta.layers/types、count 字段对 /api/stats 与外部有价值 |
| 5 | term_en 丢失 | 补 term_en 导出，删 4 处 fallback | **补依据**：后端 `term_zh or term` 已保证非空，故前端 fallback 可删 |
| 6 | graph-data.js/json 双份 | 砍 graph-data.js | 论证改为"回退边际价值不值得 706KB 双份存储"（非"不可达"） |

## 待决策项

### 待决策 A：API 去留的性价比（#1）

用户已表态"有未来消费者，希望被调用"。审查补充的权衡事实：
- API 本质是"对静态 JSON 的服务端过滤"。数据 push 触发更新，无实时性。
- 外部消费者拿全量 706KB JSON 自己 filter，与调 API 拿过滤结果，差别仅是省客户端几行 filter 代码。
- 维护成本：systemd 常驻服务 + nginx 反代 + 进程监控 + api.py 代码。

**选项**：
- A1（默认，尊重用户意愿）：保留 API + 补 `load()` 缓存。接受维护成本换"对外友好查询接口"。
- A2（降级）：冻结 API 代码与文档，但不积极维护 systemd；外部消费者暂用静态 JSON。待真有消费者再激活。
- A3（砍）：删 api.py + systemd + nginx 反代 + 弹窗。仅留静态 JSON。

**推荐**：A1。用户明确要对外，且补缓存后维护成本可控。但请用户在知情上述权衡后确认。

### 待决策 B：文章数据归属（#2）

用户已选"方案乙"（文章公开，留 JSON+API，砍 articles.js）。审查补充的代价：
- 方案乙让 graph-data.json **耦合两种更新频率的数据**（图谱稳定、文章增删频繁）。当前 1 篇无所谓，文章量上来后每次文章更新都重生成全量 JSON。
- 原 articles.js 独立加载其实是**关注点分离**设计，方案乙为消冗余砍了它。

**选项**：
- B1（方案乙，用户原选）：文章进 graph-data.json + API，砍 articles.js。最少冗余（1 份），但数据层耦合。
- B2（中间项，审查推荐）：文章**退出** graph-data.json（恢复数据层纯净）；前端 articles.js 独立加载（保持关注点分离）；API 新增 `/api/articles` 端点对外提供。产物 2 份（JS + API 端点），但数据层不耦合。
- B3（方案甲）：文章退出 JSON+API，只留 articles.js。恢复边界但外部拿不到。

**推荐**：B2。最符合第一性分层--图谱数据纯、文章独立、对外可得。代价是多一个 API 端点 + 保留 articles.js，但换来数据层干净。若用户更看重"最少产物"，选 B1。

## 文件级改动清单

> 以下按"待决策项取推荐值 A1+B2"写。若用户选其他，#1/#2 相关行相应调整。

### `scripts/export_graph.py`

1. **节点新增 `term_en`**（split_term 已解析于 265 行）：写入 node dict。
2. `layer_label` 保留（既有，作详情页权威）。
3. **不新增 `type_label`**（审查撤回--展示泄漏数据层）。
4. **若选 B2**：`export_articles` 保留写 articles.js（前端独立加载），entity_articles **不嵌入** graph-data.json（恢复数据层纯净）。
5. **若选 B1**：`export_articles` 不写 articles.js，entity_articles 嵌入 graph-data.json。
6. **main() 不再写 graph-data.js**（删 356-360 行），只写 graph-data.json。
7. `depends_on_count`/`depended_by_count`/`meta.layers`/`meta.types`：保留（#4）。

### `visualization/index.html`

1. `loadData`：删 catch 里 `window.GRAPH_DATA` 回退（331-335），fetch 失败 throw。
2. **若选 B2**：保留 `<script src="articles.js">`（785）；`articleMap` 保留 articles.js 回退。
3. **若选 B1**：删 `<script src="articles.js">`；`articleMap` 只用 `data.entity_articles`。
4. 删 CSS `.type-colors` 块（30-39，死代码）。
5. `TYPE_COLORS` / `TYPE_LABELS`：**保留**（展示层，单一来源已在 JS）。
6. `LAYER_LABELS`：**保留供 tab 短标签**；详情页/面包屑改用 `node.layer_label`（后端权威）。非一刀切。
7. term 显示：详情头用 `n.term_en` 显示英文（597-598），删 4 处 `n.term_zh || n.term` fallback。**依据**：后端 `term_zh or term`（284 行）已保证非空。

### `api.py`

1. `load()` 加内存缓存 + mtime 失效（每次请求全量 parse 706KB 扛不住对外）：
   ```python
   _cache = {"mtime": None, "data": None}
   def load():
       if not DATA_FILE.exists():
           return {"nodes": [], "edges": [], "meta": {}}
       mtime = DATA_FILE.stat().st_mtime
       if _cache["data"] is None or mtime != _cache["mtime"]:
           _cache["data"] = json.loads(DATA_FILE.read_text())
           _cache["mtime"] = mtime
       return _cache["data"]
   ```
   多 worker 下各进程独立缓存 + mtime 一致失效，无碍。
2. **若选 B2**：新增 `GET /api/articles` 端点（返回全部文章 + entity_articles 映射），`/api/nodes/{id}` 的 articles 改从 articles.yaml 派生或该端点查。
3. **若选 B1**：articles 返回保留（从 graph-data.json 的 entity_articles）。

### `CLAUDE.md`

1. "文章引用系统"章节：按 B1/B2 调整"安全边界"描述（现状"不含文章数据"已与实现矛盾，必须改）。
2. "可视化系统与部署"章节：`export_graph.py` 产物去掉 graph-data.js（砍）；articles.js 按 B1/B2 调整。
3. 部署触发路径：无需改。

### `.github/workflows/deploy-visualization.yml`

**无需改**（rsync --delete 自动清理；触发路径不含 graph-data.js/articles.js）。

## 行为变化（需知悉）

1. **前端详情页层级标签**："定义" -> "定义层" 等（详情对齐后端 layer_label）；**tab 标签不变**（保留短标签，护移动端布局）。
2. **前端英文显示修复**：详情头从 "行动者 (Agent)" 整串 -> "行动者" + "Agent"（term_en 补全）。

## 验证

1. `python scripts/export_graph.py` 重新生成，确认不再生成 graph-data.js（B1 还无 articles.js）。
2. 本地起 `index.html`：渲染正常、tab 仍短标签、详情显示"定义层"+英文、无 articles.js 依赖（B1）/ 有（B2）。
3. 本地起 `api.py`：`/api/stats`、`/api/nodes/{id}` 正常；重复请求确认缓存命中；B2 加验 `/api/articles`。
4. 验外部视角：CORS、`/api/nodes/{id}` 真实路径。
5. `python scripts/validate.py` 跑通（不碰 YAML，应无影响）。

## 不做（边界）

- 不碰 YAML 实体层。
- 不改 API 端点结构（B2 仅**新增** /api/articles，不动既有 7 个）。
- 不引入构建工具（index.html 维持零构建单文件）。
- #4 冗余字段保留。

## 审查遗留

- 本方案经出方案者自审（第一性原理），**未经独立子 Agent 复审**。L3/L4 的独立审查机制不直接适用于重构方案，但若要更严可派子 Agent 复审。
