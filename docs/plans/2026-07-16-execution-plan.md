# 执行计划：最终整合方案落地（2026-07-16）

> 依据：`2026-07-16-final-plan.md`（第一性整合方案）
> 制定：2026-07-16 · 状态：**待用户指令启动，暂不执行**
> 制定者：小敏 · 决策者：黄谦敏

## 〇、执行总则

1. **红线不动**：Author/Review 永远 pro 承重墙；Review 与 Author 异血统；反例猎捕硬门；Finalize 永远脚本；审查干预只朝严；不用付费 deepseek。
2. **标准管线强制**：清存量必须走 `ded_pipeline` / `l2_verify` / `l4_pipeline`，YAML 已存在的实体用 `skipAuthor: true`，禁止自定义一次性 Workflow。
3. **节奏区分**（关键）：
   - **修洞阶段（改管线代码）**：每项改完 -> A/B 验证 -> **报结果给你过目** -> 确认后才默认开/进入下一项。基建改动不是例行关卡，改错影响全产出。
   - **清存量阶段（走标准管线跑推论）**：按既定授权自主跑，独立审查判 `verified` 即自主翻牌+提交，`rejected` 上报你。不路由每个例行关卡（参见 `feedback-axiomatics-follow-rules-no-ask`）。
4. **熔断**：每步预估耗时见各节。超出预估则停下重新思考，不硬推。
5. **子 Agent 分发**：所有 Review/审查段必须派**全新独立上下文的子 Agent**（作者≠审查者，防自欺结构保证）。main loop 只编排/守门，不自己当审查者。

## 一、第零步：校正基线 · 预估 5min

```bash
python scripts/index.py
python scripts/export_graph.py
python scripts/validate.py
```

**验收**：
- INDEX.md 实体数更新到真实值（预期 ~261+，非 237）
- validate.py 退出码 0
- 拿到准确的 candidate / weakly_verified 清单（第二阶段排期输入）

**产出**：一份 candidate 清单（5 L4 + 2 L3 + 20 L2 + 5 weakly），贴给你确认。

---

## 二、第一阶段：补防自欺结构的洞 · 预估 3-4h（分散做）

> 第一性裁决的执行：先修洞，再清存量。四项几乎不花 AFP（仅 A/B 验证花少量）。顺序 Q1 -> C2 -> Q2 -> C1，互相独立。

### Q1 强制 Review 异血统 · 预估 40min

**改动点**（执行时先 Read 确认当前结构再改）：
- `scripts/ded_pipeline.workflow.js` / `l4_pipeline.workflow.js` / `l2_verify.workflow.js`：`reviewModel` 从"缺省继承主模型"改为"**缺省报错**"。
- 新增厂商识别映射（可放共享配置）：
  - `glm-*` = 智谱系 / `minimax-*` = minimax 系 / `doubao-*` = 豆包系 / `kimi-*` = 月之暗面系 / `sensenova-*` = 商汤系 / `deepseek-*` = deepseek 系
- 加校验：reviewModel 与主模型同厂商 -> 报错拒绝跑。

**A/B 验证**（花少量 AFP）：
- 拿 1 条 L3 candidate（DED-035 或 DED-039）。
- 路径 B（新法）：glm-5.2 Author + **minimax-m3 Review**（异血统），派独立子 Agent 审查。
- 对比历史 deepseek-v4-pro 产出：Review 是否抓到有效反例、裁决是否合理不漏水。
- **验收**：minimax-m3 能产出非空 `counterexample_hunt` + 合理裁决。若质量明显不行 -> 切 kimi-k2.7（4.5 档，更强更贵）再验。
- **过目**：A/B 结果报你，确认 minimax-m3 可用后再把 Q1 默认开启。

### C2 flash_revise 定向 patch · 预估 50min（最复杂）

**改动点**：
- `scripts/flash_revise.py`：当前 flash 输出**完整 YAML**（150-200 行）覆写文件 -> 改为输出**字段级 patch**（"定位字段 -> 新内容"对或 JSON Patch）。
- 新增 Python patch 应用器：读 patch -> 定位修改 -> 写回，不动清单外字段。
- cross-check 模式两家都输出 patch，一致才应用。

**验证**（无 A/B，机械段）：
- 构造测试：1 条 needs_revision 的 L2 桥，flash_revise 输出 patch -> 应用 -> `validate.py` 通过 -> 对比旧法覆写结果字段一致。
- **验收**：①输出 token 下降（对比旧法全文输出）②无字段丢失 ③validate 通过 ④patch 应用后内容与旧覆写语义一致。
- **A/B 实测（2026-07-16，DED-035 + 5 条 should fixes）**：
  - 输出 token：overwrite 16533 vs patch 4593-6665，**patch 省 60-72%** ✓
  - validate 通过率：overwrite 2/3（~33% 失败，flash 重排全文偶坏格式）vs patch 2/2 全过 ✓
  - 字段丢失：patch `untouchedOk=true` 结构强制无丢失；overwrite 概率性 ✓
  - 字段覆盖可审计：patch 显式 `patchFields`（2-4 字段，有波动但可审计）；overwrite 全文重写难判漏改 ✓
  - 结论：**patch 模式优于 overwrite**（更省、更稳、更安全、可审计）。flash 漏判字段是理解问题非机制问题，overwrite 同样有且更难发现。
- **过目**：A/B 结果报你确认，确认后改 workflow 默认 `--mode patch`。

### Q2 verified 反例猎捕机器校验 · 预估 20min

**改动点**：
- `scripts/finalize.py`：翻 `verified` 前，读对应审查档该 round 的 `counterexample_hunt`，**空则拒绝翻牌**、退回审查（不朝松方向，符合红线）。
- 执行时先 Read 一份现有审查档（`L3-deductions/reviews/ADV-REVIEW-*.yaml`）确认 `counterexample_hunt` 字段路径。

**验证**：
- 构造 1 份 `counterexample_hunt` 为空的审查档 -> finalize 应**拒绝**翻牌。
- 构造 1 份非空档 -> finalize 应**通过**。
- **验收**：空档被拒、非空档通过。
- **过目**：报你确认。

### C1 freeDraft 加强 · 预估 35min

**改动点**：
- `scripts/author_draft.py`：当前 `SLIM_CHECKLIST` 精简 + 没给父推论摘要 -> 加强 prompt：①父推论摘要行 ②完整 author-checklist ③瘦身 canonical 格式示例。
- 执行时先 Read `author_draft.py` + `docs/pipeline/author-checklist.md` 确认当前 prompt 结构。

**A/B 验证**（花少量 AFP）：
- 拿 1 条 L3 candidate。
- 路径 A：freeDraft off（pro 从零创作）。
- 路径 B：freeDraft on（author_draft.py 出初稿 -> pro 编辑）。
- 对比：pro 段 token 消耗 + 产出质量（是否 needs_revision）。
- **验收**：B 产出质量不差于 A，且 pro token 省 30%+。若质量差 -> **不默认开**，保留 pro 从零创作（红线不妥协）。
- **过目**：A/B 结果报你，确认后才改 workflow 默认 `freeDraft: true`。

### 配套：model-selector.yaml · 预估 15min

- 新增 `scripts/model-selector.yaml`：按时效（折扣期/折扣后）+ 血统要求，自动选 Author×Review 异血统组合（合并旧 C3）。
- 内容即 final-plan 第四节承重墙矩阵。
- workflow 读它选模型，避免 8/9 后忘切多花 4 倍。

### 第一阶段收尾冒烟 · 预估 20min

- 1 条 L3 走全流程（Author glm-5.2 -> Review minimax-m3 异血统 -> flash_revise patch -> finalize 带反例猎捕校验）。
- `validate.py` + `index.py` 通过。
- **验收**：全流程跑通，四项改动协同无冲突。
- **过目**：冒烟结果报你，确认后进入第二阶段。

---

## 三、第二阶段：清存量 · 预估 2-3 天（自主跑，verified 自主升级）

> 用修好的管线清存量。按价值×紧急排序。走标准管线，独立审查判 verified 即自主翻牌+提交，rejected 上报你。

### 前置：Q3 L2 加 revise loop · 预估 30min

- `scripts/l2_verify.workflow.js`：引入可选 revise loop（复用 flash_revise.py 免费段）+ 二轮 Review，结构与 L3 对齐。
- 这是 L2 20 条清存量的**前提**（否则半成品堆主循环）。
- 改完跑 1 条 L2 冒烟，过目后批量。

### 清存量批次（自主跑）

| 批 | 内容 | 管线 | 预估 AFP | 自主？ |
|---|---|---|---|---|
| 1 | L4 candidate 5 条（L4-014/016/017/018/019） | `l4_pipeline` | ~410 | verified 自主升级，rejected 上报 |
| 2 | L3 candidate 2 条（DED-035/039） | `ded_pipeline` | ~88 | 同 |
| 3 | weakly_verified 5 条补锚升级 | `ded_pipeline` skipAuthor | ~110 | 同 |
| 4 | CNBS 改造 P0-P3 | 见 `cnbs-tools-system-improvement-plan` | ~55 | 按 CNBS 方案 |
| 5 | L2 candidate 20 条（BR-L2-033~052） | `l2_verify`（Q3 后） | ~280 | 同 |

**批次间纪律**：
- 每批结束跑 `validate.py` + `index.py`。
- 5h/1 万 AFP 突发：每批别超 ~40 条，S3 并发治理后分批。
- 管线故障重跑用 `resumeFromRunId` 白拿缓存，禁整重跑。

---

## 四、第三阶段：增量扩展 · 富余 AFP，折扣窗口末

- EMP-TEST 4 -> 10+ 条（深度经验检验）
- 跨源验证模式落地（CNBS P3 方法论资产）
- 补 L3 / L4 缺口
- 自主跑，verified 自主升级。

---

## 五、8/8 折扣节点检查清单

8/8 前必须做完的（按优先级保底）：
1. ✅ 第一阶段修洞（Q1/C2/Q2/C1）-- **必做**，否则后续产出是假独立审查
2. ✅ L4 5 条 + L3 2 条清存量（最高价值）
3. ⏳ weakly 5 条 + CNBS（能做就做）
4. ⏳ L2 20 条（可延后到折扣后，L2 单条最便宜）

8/8 后：承重墙切 doubao（Author）+ minimax（Review），`model-selector.yaml` 自动切换。

---

## 六、熔断与暂停点

- **修洞阶段**：每项 A/B 验证后**暂停过目**（4 个暂停点：Q1/C2/Q2/C1 各一 + 收尾冒烟一）。
- **清存量阶段**：自主跑，仅在 rejected / 管线故障 / 撞 AFP 突发限时停。
- **任何阶段超预估 1.5 倍**：停下重新思考，不硬推（熔断原则）。

---

## 七、执行状态

- [x] 整合方案制定（`2026-07-16-final-plan.md`）
- [x] 执行计划制定（本文件）
- [x] 用户确认落盘、暂不执行
- [x] 用户指令启动（2026-07-17凌晨,授权自主清存量）
- [x] 第零步：index.py 校正基线（283实体）
- [x] 第一阶段 Q1：强制异血统 + A/B 通过（review_minimax.py MiniMax-M3）
- [x] 第一阶段 C2：flash_revise patch + A/B 通过 + workflow 已开 --mode patch（省 60-72% token + validate 更稳 2/2 vs 2/3）
- [x] 第一阶段 Q2：反例猎捕硬门 + 验证通过（空/敷衍被拒,非空通过,历史 ADV-013 敷衍 verified 被拒）
- [~] 第一阶段 C1：freeDraft 加强（延后,需A/B过目,用户不在跳过）
- [ ] 第一阶段配套：model-selector.yaml（8/8前做）
- [x] 第一阶段收尾冒烟=L4-018 走全流程 verified（Q1+C2+Q2 协同通）
- [x] 第二阶段前置：Q3 L2 revise loop（revise_loop.py 编排替代,L2已跑通）
- [x] 第二阶段清存量(2026-07-17凌晨自主):2 verified(L4-018+BR-L2-029)/1 rejected(BR-L2-025 DED-007复发,上报用户)/5 needs_revision停(L4-016/017/019+DED-039+BR-L2-031)/1 weakly未升(BR-L2-032)
- [ ] 第三阶段：增量扩展
- [ ] 8/8 节点：承重墙切 doubao+minimax
