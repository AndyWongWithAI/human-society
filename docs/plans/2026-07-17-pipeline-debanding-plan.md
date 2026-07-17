# Pipeline 去包裹层成本优化 Plan

> 2026-07-17 制定。承接 [[feedback-pipeline-cost-estimation]] 的 108 倍误差根因诊断，
> 取代 [[2026-07-16-pipeline-optimization]] 里"换模型/错峰"等未触及根因的旧措施。
> 完整方案文档本档;执行节奏见末节。

## 0. 摘要(一句话)

把 7 个当"命令执行器"的 glm-5.2 包裹层 workflow agent 换成 Python `subprocess`,
单条推论成本从 **137.71 AFP** 降到约 **20-35 AFP**(-75~85%),质量红线(异血统承重墙
+ 作者≠审查者)不动。核心不是换模型,是**不再用大模型跑 bash**。

## 1. 背景与诊断

### 1.1 实测基线(来自 feedback-pipeline-cost-estimation,2026-07-17)

| 指标 | 10 条合计 | 平均/条 |
|---|---|---|
| 方舟 glm-5.2(折后 AFP) | 1377.06 | **137.71** |
| minimax-M3(weekly 配额) | +1% | ~0.1%/条 |
| 免费模型(Revise 双厂商) | 0 | 0 |
| 墙钟(3 条并行批) | 49.3 min | 4.9 min/条 |

glm-5.2 占成本 ~99%。之前用"单步 Author × 条数"估算得 1.28 AFP/条,差 **108 倍**。

### 1.2 108 倍误差根因:用 glm-5.2 当命令执行器

`ded_pipeline.workflow.js` / `l4_pipeline.workflow.js` 的每一轮 Review/Revise/Finalize
都外包一层 `await agent(...)`(底层 glm-5.2)去跑一条 python 脚本:

```
Author:     1 个 glm-5.2 agent(创作,该花)
Review×3:   3 个 glm-5.2 包裹 agent(跑 review_minimax.py)  ← 不该花
Revise×3:   3 个 glm-5.2 包裹 agent(跑 flash_revise.py)    ← 不该花
Finalize:   1 个 glm-5.2 包裹 agent(跑 finalize.py)        ← 不该花
──────────────────────────────────────────────────────────
每条 ≈ 8 个 glm-5.2 agent,其中 7 个在当"bash 命令执行器 + JSON 解析器"
```

这 7 个包裹层做的事(跑脚本 + 读 stdout JSON + 回填 schema)**不需要任何 LLM 推理**,
用 `subprocess` 就够了。37 subagent / 557 tool calls / 971k subagent_tokens 全是
glm-5.2 在"思考怎么跑一条命令"。

### 1.3 旧优化措施为何不触及根因

[[2026-07-16-pipeline-optimization]] 的 7 项措施(Finalize 脚本化/resume 重跑/阅读包/
红旗回灌/Revise 下放 flash/商汤侧翼/错峰)都是**在 workflow 框架内省 token**,没有
动"包裹层本身不该是 LLM"这个根。Finalize 脚本化已做(✓),但 Finalize 外面仍套着一层
glm-5.2 agent 跑 `finalize.py`--脚本化了却还用大模型去调用脚本,收益被包裹层吃掉。

## 2. 第一性原理:阶段认知能力 × 模型 × 思维链分级

把 pipeline 拆到原子,逐阶段问"本质上需要什么能力":

| 阶段 | 认知本质 | 需要的能力 | 思维链 | 当前实现 | 问题 |
|---|---|---|---|---|---|
| Author | 创造性合成:父推论机制 → 新可证伪命题 | 深度推理+创造力+格式遵循 | **需要(high)** | glm-5.2 workflow agent | 必要消耗,freeDraft 已省 30-50% |
| Review | 反例猎捕 + 16 红旗对抗 | 深度推理+怀疑思维+**异血统** | **需要** | minimax-M3(Python 直调) | ✅ 已最优 |
| Revise | 按清单改 YAML 字段 | 几乎零推理(机械执行) | **不需要(none)** | 免费模型(Python 直调) | ✅ 已最优 |
| Finalize | 翻 status + validate | 零推理 | 无模型 | Python 脚本 | ✅ 已最优 |
| **包裹层编排** | 跑脚本 + 解析 JSON | **零推理** | 不需要 | **glm-5.2 workflow agent** | ❌❌ 杀鸡用牛刀 |

**关键发现:`blind_coder.py` 已证明 Python 直调层思维链可控**(`reasoning_effort: "none"`
关掉 glm 默认思维链)。而 workflow agent 层思维链在脚本层**关不掉**(`await agent()`
无 thinking 开关)。这从另一个侧面证明:要去掉无谓思维链消耗,必须去包裹层。

## 3. 硬约束(来自记忆,不可绕过)

| 约束 | 来源 | 对本 plan 的影响 |
|---|---|---|
| workflow agent 底层全 glm-5.2,传任何 model 都路由到 glm-5.2 | [[minimax-access-constraint]] | 包裹层换不了模型,只能去掉 |
| 异血统只能靠 Python 脚本直调 minimax | 同上 | Review 必须留 Python 直调,不能回 workflow |
| minimax 不宜当 Author(YAML 格式失败+validate 静默吞错) | [[human-society-model-swap-verdict-2026-07]] | Author 保持 glm-5.2 |
| Author=glm-5.2 × Review=minimax 异血统是承重墙 | [[human-society-final-plan]] Q1 | 角色**不互换** |
| 标准管线强制:必须走标准脚本,禁自定义 Workflow | 项目 CLAUDE.md | 本 plan 是 Python 串联,符合 |
| 方舟同时只能激活一个模型(当前 glm-5.2 锁定) | [[minimax-access-constraint]] | Python 直调 glm-5.2 走 SenseNova 网关,不争抢激活位 |

**结论:"把 glm-5.2 换成 minimax"在当前架构下无可操作空间**(Review 已是 minimax,
其余全免费,包裹层换不了,Author 换 minimax 有格式硬伤)。真正的杠杆是**去掉包裹层**,
而非换模型。

## 4. 方案:去包裹层,全链路 Python 串联

### 4.1 核心思路

把 `ded_pipeline.workflow.js` 的 4 个 phase 从"workflow agent 编排"改为"Python
subprocess 串联"。每个阶段的原有 Python 资产(review_minimax / flash_revise / finalize)
**全部保留不改**,只去掉套在外面的 glm-5.2 agent 壳。

### 4.2 目标架构(分层不变,只换编排层)

```
L1 原子组件(不动):
  author_draft.py    免费模型出骨架(freeDraft,reasoning_effort=none)
  author_pro.py      [新] glm-5.2 编辑成稿(reasoning_effort=high)  ← 唯一新组件
  review_minimax.py  minimax-M3 异血统审查(不动)
  flash_revise.py    免费模型整改(加 reasoning_effort=none,不动逻辑)
  finalize.py        脚本翻牌(不动)

L2 编排组件:
  revise_loop.py     Phase 2-3 编排(已有,不动)
  run_pipeline.py    [新] 全链路薄编排:author_pro → revise_loop  ← 唯一新编排
```

分层守恒:L1 原子只被 L2 编排引用,L2 不被 L1 引用,无循环。`run_pipeline.py` 是薄壳,
不重新实现审查/整改逻辑,只组合 L1。

### 4.3 模型 × 思维链 最终矩阵

| 阶段 | 模型 | 接入 | reasoning_effort | 血统 | 成本 |
|---|---|---|---|---|---|
| freeDraft 骨架 | deepseek-v4-flash | SenseNova 网关 | none | DeepSeek 系 | 免费 |
| Author 成稿 | **glm-5.2** | SenseNova 网关 | **high** | 智谱系 | 付费(唯一付费点) |
| Review | **MiniMax-M3** | minimax Anthropic 兼容 | (启用 thinking,见措施4) | minimax 系 | 极廉(weekly 配额) |
| Revise | sensenova+zhipu 双厂商 | SenseNova/智谱 | none | 双免费 | 免费 |
| Finalize | 无模型 | Python | - | - | 免费 |

异血统矩阵:Author(智谱)× Review(minimax)× Revise(DeepSeek+智谱)= 三血统独立,承重墙不塌。

## 5. 具体措施

### 措施 0:前置验证(大半已完成)

| 验证项 | 状态 | 结论 |
|---|---|---|
| glm-5.2 能否 Python 直调 | ✅ blind_coder.py 已证 | 经 SenseNova `base_url/chat/completions`,model 传 `glm-5.2` |
| 思维链能否 Python 层控制 | ✅ blind_coder.py 已证 | `reasoning_effort: "none"/"high"` |
| minimax Python 直调 | ✅ review_minimax.py 已证 | Anthropic 兼容接口 |
| 方舟激活位是否被争抢 | ✅ 已证 | Python 走 SenseNova 网关,不争抢方舟激活位 |
| **author_pro.py 能否输出完整合规 YAML** | ⚠️ **待 A/B 验证** | glm-5.2 纯 Python 直调输出完整 canonical YAML 的格式遵循度,是本 plan 最大风险点 |

措施 0 的最后一项并入措施 1 的 A/B 验证,不单独跑。

### 措施 1:写 `author_pro.py`(新 L1 原子资产)

**定位**:Author 阶段的 Python 化。freeDraft 出骨架 → glm-5.2 编辑成稿。

**设计**(仿 `author_draft.py` 结构,接 `blind_coder.py` 的 glm-5.2 接入):
- 接入:读 `secrets.json["sensenova"]` 的 base_url + api_key,model 传 `glm-5.2`(仿 blind_coder.py:16-17,107-120)
- 思维链:`reasoning_effort: "high"`(Author 是创作,唯一需要思维链的付费阶段)
- 输入:brief JSON + `author-pack.md` 全文 + freeDraft 骨架文件(若有)
- 输出:完整 canonical YAML,写到 `L3-deductions/corollaries/<id>-<slug>.yaml` 或 L4 对应目录
- 复用 `author_draft.py` 的 `SLIM_CHECKLIST` / `extract_yaml` / system prompt(不重复造)
- **YAML 严格前置门**(吸收 [[human-society-model-swap-verdict-2026-07]] 教训):写文件前
  `yaml.safe_load` 自检,失败则把错误回灌模型重试(最多 2 次),仍失败返回 `author_failed`
- 跑 `validate.py`,返回 `{done, draftPath, validatorOk, note}`
- 支持 `--layer L3/L4`,L4 追加 `l4-author-checklist.md`

**与 author_draft.py 的关系**:author_draft.py(免费骨架)保留不动,author_pro.py 在其上层。
freeDraft=true 时 run_pipeline 先调 author_draft.py 出骨架,再调 author_pro.py 编辑;
freeDraft=false 时 author_pro.py 直接从零创作。

### 措施 2:写 `run_pipeline.py`(新 L2 编排资产)

**定位**:全链路薄编排,替代 `ded_pipeline.workflow.js` / `l4_pipeline.workflow.js`。

**设计**(仿 `revise_loop.py` 的 subprocess 串联风格):
```
run_pipeline.py <id> --layer L3/L4 --review-num <n> --brief-file <path> [--freeDraft] [--max-rounds 3]
  1. (若 freeDraft) subprocess 调 author_draft.py 出骨架
  2. subprocess 调 author_pro.py 编辑成稿(validate 过)
  3. 调用 revise_loop.py(已实现 Phase 2-3:Review-Revise-Finalize 全套)
  4. 汇总输出 {id, verdict, rounds, paths, core}(与 workflow 返回结构兼容)
```

**复用而非重写**:Phase 2-3 完全委托 `revise_loop.py`(已有,含崩溃恢复/幂等/重试),
run_pipeline.py 只负责 Author 段 + 衔接。**不重新实现审查/整改/定论**。

**回退路径**:run_pipeline.py 与 ded_pipeline.workflow.js 返回结构兼容,A/B 期间可随时
切回 workflow 路径,不影响主循环消费。

### 措施 3:思维链分级固化(改 3 个现有脚本,各 1 行)

| 脚本 | 改动 | 理由 |
|---|---|---|
| `flash_revise.py` `call_flash` | 加 `"reasoning_effort": "none"` | 整改机械执行,关思维链 |
| `iea_survey.py` `call_free_model` | 加 `"reasoning_effort": "none"` | 来源定性判断+算术,关思维链 |
| `author_draft.py` `call_free_model` | 加 `"reasoning_effort": "none"` | 免费骨架,关思维链 |

(免费模型本就无强思维链,但显式设 `none` 防个别模型默认开,且统一可读。)

### 措施 4:Review 显式启用 thinking(可选,提质量非降本)

`review_minimax.py` 当前用 minimax Anthropic 兼容格式未传 thinking 参数。minimax-M3
作为 reasoning 模型,显式启用 thinking 可提升反例猎捕深度。成本可忽略(10 条仅 1% weekly,
即使翻倍仍 2%)。

**前置**:确认 minimax Anthropic 兼容接口的 thinking 参数格式(`thinking.type=enabled`,
`budget_tokens`)。若接口不支持则维持现状(minimax-M3 可能默认已带 reasoning)。

**优先级**:低于措施 1-3。措施 1-3 是降本,措施 4 是提质量。先拿降本数据,再决定是否提质量。

## 6. A/B 验证设计

### 6.1 验证目标

证明"Python 全串联"在**质量不降**的前提下达成**降本**。质量红线:审查 verdict 不差于
workflow 路径,validate 通过,字段完整。

### 6.2 验证方法

选 1 条**新命题**(非存量重审,避免缓存干扰),同 brief 跑两条路径:

| 路径 | 执行 | 预期 AFP |
|---|---|---|
| A(对照) | `ded_pipeline.workflow.js` | ~138(基线锚点) |
| B(实验) | `run_pipeline.py --freeDraft` | ~20-35 |

对比维度:
1. **成本**:方舟 AFP 消耗、minimax weekly 占比、总墙钟
2. **质量**:产出 YAML 字段完整度、validate 是否通过、Review verdict 与轮数、反例猎捕质量
3. **格式稳健性**:author_pro.py 的 YAML 一次过率(措施 1 最大风险)

### 6.3 通过判据

- B 的 Review verdict ≥ A(不更严即不降质,更严则证明质量提升)
- B 的 validate 通过、字段完整
- B 的方舟 AFP < A 的 40%(即降幅 >60%,达预期 75-85% 的下限宽容)
- author_pro.py YAML 一次过率 ≥ 80%(否则需加修复轮)

### 6.4 暂停点

按 [[human-society-final-plan]] 节奏,A/B 验证后**暂停过目**,不自主切换。用户确认后再
批量推广。

## 7. 预期效果

| 指标 | 当前(workflow 路径) | 优化后(Python 全串联) | 降幅 |
|---|---|---|---|
| 每条 glm-5.2 agent 数 | ~8(1 Author + 7 包裹) | **1**(仅 Author,且 freeDraft 省 30-50%) | -87% |
| 单条方舟 AFP | 137.71 | **~20-35** | **-75~85%** |
| 墙钟/条(并行) | 4.9 min | 预计相近或略降(subprocess 无 agent 冷启动) | 0~-20% |
| Review 血统 | minimax 异血统 | **不变** | - |
| Author 质量 | glm-5.2 pro | **不变**(仍是 glm-5.2,带思维链) | - |
| 防自欺结构 | 作者≠审查者+异血统 | **不变** | - |

**月度外推**:若月 10 万 AFP 预算,当前可买 ~725 条 L3;优化后可买 ~2900-5000 条(4-7 倍
吞吐),或同等吞吐下月省 7-8 万 AFP。

## 8. 质量红线核对(逐条)

| 红线(来自项目 CLAUDE.md / final-plan) | 本 plan 是否触碰 |
|---|---|
| 方法论质量 > 任何单条推论 | ✅ 不碰,Author 仍 pro glm-5.2 + 思维链 |
| 作者≠审查者(防自欺结构) | ✅ 不碰,Author(glm-5.2)与 Review(minimax)仍不同主体 |
| Review 永远是 pro 承重墙 | ✅ 不碰,Review 仍 minimax-M3 |
| Review 异血统(ICV 协议) | ✅ 不碰,Author 智谱 × Review minimax |
| Finalize 永远是脚本 | ✅ 不碰 |
| 审查裁决干预只允许朝更严方向 | ✅ 不碰(本 plan 不涉及裁决干预) |
| 标准管线强制 | ✅ 符合,Python 串联是标准脚本,非自定义 Workflow |

**所有红线零触碰。** 本 plan 只动"编排层用什么跑脚本",不动"谁审查/谁创作/什么血统"。

## 9. 风险与回滚

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| author_pro.py 输出 YAML 格式不合规(glm-5.2 纯 Python 直调未验证过完整 YAML) | 中 | 高(Author 段失败) | 措施 1 内置 YAML 严格前置门 + 错误回灌重试;A/B 先验,不达标不切 |
| glm-5.2 经 SenseNova 网关的 reasoning_effort=high 实际效果未验 | 低 | 中(思维链没开起来,质量退化) | A/B 对比 Author 产出质量;可降级为 freeDraft+agent 编辑回退路径 |
| Python 串联丢失 workflow 的并行能力 | 低 | 低 | revise_loop.py 已支持并发(记忆:max_workers=5);run_pipeline 可并发多条 |
| 去包裹层后主循环失去 workflow 的结构化日志/phase 可观测 | 中 | 中 | run_pipeline.py 输出结构化 JSON + stderr 进度(仿 revise_loop.py) |
| minimax 8/16 到期不续 | 中 | 高(Review 回同血统) | 与本 plan 正交,见 [[minimax-access-constraint]];本 plan 不依赖 minimax 续费降本 |

**回滚**:保留 `ded_pipeline.workflow.js` / `l4_pipeline.workflow.js` 不删。A/B 期间
Python 串联与 workflow 并存,任何阶段不达标即切回 workflow,已产出的实体文件不受影响
(YAML 格式与路径完全兼容)。

## 10. 资产化(遵循资产原则)

| 资产 | 层级 | 定位 | 可复用范围 |
|---|---|---|---|
| `author_pro.py` | L1 原子 | glm-5.2 Python 直调 Author | L3/L4/L2 通用 |
| `run_pipeline.py` | L2 编排 | 全链路串联 | L3/L4 通用(L2 用 l2_verify) |
| 思维链分级配置(措施3) | L1 参数 | reasoning_effort 标准化 | 所有 Python 直调脚本 |

**登记**:A/B 验证通过、切换主路径后,按资产原则登记到架构平台。未通过则不登记
(不能算资产,只算实验脚本)。

**反馈机制**:若 author_pro.py 的 glm-5.2 格式遵循度持续不达标,反馈到架构平台,
决策"优化 prompt / 加修复轮 / 回退 agent 编辑模式"。

## 11. 执行顺序与暂停点

```
[暂停0] 措施3(思维链分级,3行改动)→ 跑 validate 确认不破坏
   ↓
[暂停1] 措施1(author_pro.py)→ 选1条新命题A/B
   ├─ 路径A: ded_pipeline.workflow.js(对照)
   └─ 路径B: author_pro.py 单独跑 Author 段
   对比 YAML 质量 + 格式一次过率 → 暂停过目
   ↓
[暂停2] 措施2(run_pipeline.py)→ 同命题全链路A/B
   ├─ 路径A: ded_pipeline.workflow.js
   └─ 路径B: run_pipeline.py --freeDraft
   对比 AFP + verdict + 墙钟 → 暂停过目
   ↓
[暂停3] 用户确认后,批量推广到新推论;存量重审仍用 revise_loop.py
   ↓
[可选] 措施4(Review thinking)→ 质量提升A/B
```

**熔断预估**:措施1+2 开发+A/B 约 2-3 小时。若超 4 小时未拿到 A/B 数据,停下来重新审视
(熔断原则)。

**不做什么(明确排除)**:
- ❌ 不换 Author 模型为 minimax(格式硬伤,[[human-society-model-swap-verdict-2026-07]])
- ❌ 不角色互换 Author↔Review(收益不确定,引入格式风险,不如去包裹层划算)
- ❌ 不碰 Review 血统(承重墙红线)
- ❌ 不写自定义 Workflow 绕过标准脚本(违项目 CLAUDE.md 标准管线强制)

---

**关联记忆**:
[[feedback-pipeline-cost-estimation]] · [[human-society-final-plan]] ·
[[human-society-model-swap-verdict-2026-07]] · [[minimax-access-constraint]] ·
[[axiomatics-cost-optimization-plan]]
