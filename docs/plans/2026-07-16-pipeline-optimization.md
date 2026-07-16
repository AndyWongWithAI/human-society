# 公理化管线优化方案（质量 / 速度 / 费用）

> ⚠️ **已被 [`2026-07-16-final-plan.md`](2026-07-16-final-plan.md) 取代**（2026-07-16 第一性整合）。本文件保留作决策过程记录。
> 制定：2026-07-16 · 状态：~~待用户指令启动~~ → 已被整合方案取代
> 制定者：小敏（Claude Code）· 决策者：黄谦敏
> 审查范围：管线脚本与配置（非数据），已读透 3 标准管线 + 2 批量 + 7 Python 脚本 + 4 评分卡/清单 + 2 方法论
> 关联：`2026-07-16-afp-budget-plan.md`、`axiomatics-cost-optimization-plan`、`axiomatics-pipeline-use-workflow`

## 一、管线健康度总评

**地基扎实**：作者≠审查者、fresh 上下文、反例猎捕硬门、双厂商交叉验证、confidence_floor 跨层传播、审查干预只准朝严--防自欺结构成体系。成本优化 7 项已落地 4 项（finalize 脚本化 / 阅读包 / flash 下放 / 异血统）。**管线本身不是瓶颈，AFP 更不是。**

结构性缝隙按三维度展开如下。

## 二、质量维度

### Q1 承重墙血统独立性未强制（最大质量洞）· P0

**问题**：三条 workflow 里 `reviewModel` **可选**，不设则"继承主模型"。当前 glm-5.2 做 Author，若 Review 也 glm-5.2 = **同血统自审**。L3-METHODOLOGY ICV 协议明文："同血统=相关错误，独立价值低""自审是假的承重墙"。管线默认配置恰好落进方法论自己警告的陷阱。

**措施**：强制 `reviewModel` 异血统。折扣期 Author=glm-5.2（智谱系），Review=minimax-m3 或 kimi-k2.7（不同厂商）。把"reviewModel 缺省=报错而非继承"写进 workflow。

**收益**：审查从"上下文独立"升级为"上下文+血统双独立"，verified 含金量实质上升。
**红线**：✅ 补强红线（ICV 协议本就要求），不碰"Review 永远 pro"。费用略升，该花。

### Q2 verified 的"反例猎捕"无机器校验 · P0

**问题**：评分卡要求"判 verified 前必须留下反例猎捕记录"，但 validate.py 只校结构，不查审查档 `counterexample_hunt` 是否非空。全靠审查者自觉。

**措施**：finalize.py 翻 `verified` 前，检查对应审查档该 round 含非空 `counterexample_hunt`；空则拒绝翻牌、退回审查。

**收益**：堵"敷衍型 verified"。
**红线**：✅ 补强。

### Q3 L2 管线不收敛 · P1

**问题**：L2 只 1 轮审查、无 revise loop，needs_revision 交主循环。压力测试实测 20 条桥 **0 verified / 0 rejected / 20 needs_revision**--产出几乎全是半成品，堆给主循环。

**措施**：L2 管线引入可选 revise loop（复用 flash_revise.py 免费段）+ 二轮 Review，结构与 L3 对齐。

**收益**：L2 自收敛，主循环只收终态。
**红线**：✅ 不碰。

### Q4 评分卡红旗认知负荷 · P2

**问题**：通用 16 + L4 专属 7 = 23 条红旗，一次审查逐条攻，易敷衍/遗漏。部分重叠（测量轴正交/anti-talisman/口径注册都涉操作化）。

**措施**：按"必攻核心 5-7 条 + 按 claim_type 条件触发"分层。

### Q5 finalize 覆写 review_summary 丢声明 · P2

**问题**：finalize.py 用模板覆写 `review_summary`，冲掉作者手写的累程收窄声明（author-checklist E 段要求）。

**措施**：只追加定论行，保留收窄声明；或拆 `narrowing_statement` 独立字段。

### Q6 缺跨实体语义审计 · P2

**问题**：validate.py 只校结构，不校"两条推论是否矛盾/重复/L4 涌现是否真非平凡"。审查者单条隔离，看不到全局。

**措施**：定期批量语义审计脚本，模型扫全量推论找矛盾/重复/平凡合取。

## 三、速度维度

### S1 flash_revise 双厂商串行 · P1

**问题**：cross-check 模式 sensenova 和 zhipu 串行跑，墙钟=两家之和。

**措施**：`concurrent.futures`/asyncio 并行两家。免费模型可并发。

**收益**：Revise 段墙钟减半。
**红线**：✅ 不碰。

### S2 finalize 每次重生全量 INDEX · P1

**问题**：finalize.py 默认跑 `index.py` 重生整个 INDEX.md（遍历全部 ~260 实体），每翻一条牌全量重生。

**措施**：finalize 默认 `--no-index`，批量结束后统一跑一次 `index.py`。

**收益**：单条翻牌墙钟下降，批量场景 INDEX 重生从 N 次降为 1 次。
**红线**：✅ 不碰。

### S3 批量无并发治理 · P1

**问题**：ded_batch/l4_batch 用 `parallel` 全并行。撞方舟 5h/1万 AFP 突发 + glm-5.2 RPM~20 限流时，调用失败重试浪费。

**措施**：批量管线加并发上限（semaphore 3-5）+ AFP 预算预估分批。

**收益**：避免限流失败重试，墙钟可控。
**红线**：✅ 不碰。

### S4 validate 全量扫描 · P2

**问题**：每次 finalize/flash_revise 都遍历全部实体，实体数增长后线性变慢。

**措施**：增量模式（只校受影响实体+依赖链）或分层校验（快速结构 vs 全量语义）。

### S5 iea_survey 字符截断 · P2

**问题**：`build_prompt` 对 >12000 字符桥接砖截断，可能丢 applicable_sources/falsifiability 关键内容。

**措施**：结构化提取（parse YAML 取关键字段）。免费模型 deepseek-v4-flash 有 1M 上下文，无需截断。

### S6 batch 大批量用 agent 读 briefsFile · P2

**问题**：ded_batch/l4_batch 大批量模式用 agent 读 JSON 解析 briefs，浪费一次 agent 调用。

**措施**：workflow 沙箱支持 fs 则直接读文件。

## 四、费用维度

### C1 Author 免费预草稿默认关（最大费用杠杆）· P0

**问题**：Author 段是最大成本（pro 从零创作）。`freeDraft` 实验性、**默认关**。压力测试免费模型生成质量不够（20 条全 needs_revision），但根因可能是 author_draft.py 用精简 SLIM_CHECKLIST + 没给父推论摘要，prompt 太弱，而非模型能力不足。

**措施**：加强 freeDraft prompt（父推论摘要行 + 完整清单 + 瘦身格式示例）-> A/B 验证（同一条 L3，freeDraft on vs off，比 pro 编辑 token 与产出质量）-> 验证通过后默认开。

**收益**：Author 段 pro 从"创作"降为"编辑"，省 30-50% token。
**红线**：✅ Author 仍 pro（只改编辑模式），不碰承重墙。

### C2 flash_revise 全文覆写浪费输出 · P0

**问题**：flash 输出**完整 YAML**（150-200 行）覆写文件，实际只改几处。输出 token 浪费 80%+，全文覆写有丢字段/动清单外内容风险。

**措施**：flash 输出**字段级 patch**（JSON Patch 或"定位字段->新内容"对），Python 应用 patch 而非覆写。

**收益**：输出 token ↓80%，覆写风险 ↓，墙钟 ↓。
**红线**：✅ Revise 本就是免费机械段，不动承重墙。

### C3 折扣后模型选型未内置 · P1

**问题**：workflow 的 reviewModel 由 brief 传入，无"折扣期自动 glm-5.2、8/9 后自动 doubao-seed-2.0-pro"逻辑。每次跑要人记着改。

**措施**：加 `model-selector.yaml` 配置，按时效自动选承重墙模型（呼应 AFP 预算规划）。

**收益**：避免折扣后忘切模型多花 4 倍钱。
**红线**：✅ 不碰。

### C4 Review r1 输入可精炼 · P2

**问题**：Review r1 给审查对象全文含 derivation。

**措施**：只给核心字段（statement/falsifiability/anchors），不给 derivation 全文。

### C5 blind_coder 串行 + sleep · P2

**问题**：独立模型可并行却串行。

**措施**：sensenova-lite + glm-5.2 并行，deepseek 对照并行。

## 五、优先级矩阵

| 编号 | 杠杆 | 维度 | 优先级 | 动红线？ | 预期收益 |
|---|---|---|---|---|---|
| Q1 | 强制 Review 异血统 | 质量 | P0 | 补强 | verified 真独立 |
| C1 | freeDraft 加强+默认开 | 费用 | P0 | 否 | Author 省 30-50% |
| C2 | flash_revise 定向 patch | 费用+速度+质量 | P0 | 否 | 输出 token ↓80% |
| Q2 | verified 反例猎捕校验 | 质量 | P0 | 补强 | 堵敷衍 verified |
| Q3 | L2 管线加 revise loop | 质量+速度 | P1 | 否 | L2 自收敛 |
| S1 | flash_revise 双厂商并行 | 速度 | P1 | 否 | Revise 墙钟减半 |
| S3 | 批量并发治理 | 速度+费用 | P1 | 否 | 避免限流浪费 |
| C3 | 折扣后模型自动选型 | 费用 | P1 | 否 | 防忘切多花 4x |
| S2 | finalize 默认 --no-index | 速度 | P1 | 否 | INDEX 重生 N->1 |
| Q4 | 评分卡红旗分层 | 质量 | P2 | 否 | 审查认知负荷 ↓ |
| Q5 | finalize 保留收窄声明 | 质量 | P2 | 否 | 防信息丢失 |
| Q6 | 跨实体语义审计 | 质量 | P2 | 否 | 全局一致性 |
| S4 | validate 增量校验 | 速度 | P2 | 否 | 大规模后提速 |
| S5 | iea 结构化提取 | 速度+质量 | P2 | 否 | 防截断丢信息 |
| C4 | Review r1 输入精炼 | 费用 | P2 | 否 | 输入 token ↓ |
| C5 | blind_coder 并行 | 速度 | P2 | 否 | ICV 墙钟 ↓ |

## 六、红线声明（不可碰）

以下优化**全部不碰**质量红线，Q1/Q2 是**补强**红线：

- Author/Review 永远 pro 承重墙--C1 只改 Author 为"编辑模式"，仍 pro
- Finalize 永远脚本--不动
- 审查干预只朝更严--不动
- 反例猎捕硬门--Q2 给它加机器 teeth
- ICV 血统独立--Q1 把它从"可选"变"强制"

## 七、实施顺序

**第一批（P0，折扣窗口前做完）**：Q1 -> C2 -> Q2 -> C1。互相独立，Q1/C1 是质量/费用两端最大杠杆，C2 三赢，Q2 堵漏洞。每条先 A/B 验证再默认开启（尤其 C1 freeDraft、Q1 异血统）。

**第二批（P1）**：Q3、S1、S3、C3、S2。结构性提速与防错。

**第三批（P2）**：按需，规模化后再做（S4 增量校验、Q6 语义审计在实体数翻倍后才有必要）。

## 八、执行状态

- [x] 全管线审查完成（2026-07-16）
- [x] 用户确认落盘、暂不执行
- [ ] 用户指令启动第一批
- [ ] Q1 强制 Review 异血统（+A/B 验证）
- [ ] C2 flash_revise 定向 patch
- [ ] Q2 verified 反例猎捕校验
- [ ] C1 freeDraft 加强 + A/B + 默认开
