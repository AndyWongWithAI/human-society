# 人类社会公理化体系 — 项目设计文档

> 状态: approved | 日期: 2026-07-13 | 迭代: iter-000 (设计阶段)

## 1. 项目概要

### 1.1 核心目标

基于公理，推出推论。研究对象：人类社会。

构建一套自洽的公理化体系，涵盖从个体行为到群体制度的推导链条。产出形态为知识图谱/结构化关系网络（YAML 先迭代，后期导入数据库）。

### 1.2 认识论立场 (META)

本体系**永远不完备**，每一轮迭代产出的是阶段性结论，而非最终真理。原因有三：

1. **哥德尔不完备性**：任何足够复杂的公理系统，必然存在无法从公理推出的真命题，或存在矛盾。人类社会 >> 皮亚诺算术。
2. **涌现不可约性**：宏观社会现象不完全由微观公理加总决定。复杂适应系统（CAS）的涌现属性具有向下因果力。
3. **观察者效应**：研究者在系统内部观察系统，文化预设、语言边界、时代局限构成认知天花板。
4. **历史偶然性**：路径依赖不在公理化解释范围内（公理能解释"为什么有制度"，不能解释"为什么是威尼斯不是热那亚"）。

### 1.3 成功标准 (MVP)

- **公理集收敛**：10-30 条自洽公理，每条有跨来源（演化生物学 + 博弈论 + 文化普适性）的证据支撑，公理间无矛盾
- **可验证推论**：从公理出发，推出若干条非平凡推论，能用现实社会现象（观察/人类学记录/历史数据）验证

---

## 2. 项目结构

```
research/human-society/
├── README.md                    # 项目说明 + 方法论概述
├── META.yaml                    # 项目哲学声明（不完备性、已知极限）
├── docs/
│   └── design/                  # 设计文档
├── axioms/                      # 公理层
│   ├── candidates/              # 候选公理（每条一个 YAML）
│   ├── verified/                # 已通过交叉验证的公理
│   └── rejected/                # 被否决的候选 + 否决理由
├── deductions/                  # 推论层
│   ├── theorems/                # 定理（多步推导）
│   └── corollaries/             # 推论（直接推导 + 现实锚点）
├── sources/                     # 来源层（跨学科证据）
│   ├── evolutionary-biology/    # 演化生物学证据
│   ├── game-theory/             # 博弈论证据
│   ├── cultural-universals/     # 文化普适性证据
│   └── cross-verification/      # 交叉验证记录
├── iterations/                  # 迭代快照
│   └── iter-NNN/
│       ├── snapshot.yaml        # 当前公理集/推论集全貌
│       ├── diff.yaml            # 相比上一轮的变更
│       └── CONCLUSION.md        # 阶段性结论（含已知的未知）
└── glossary/                    # 基础概念定义（拆分为独立 YAML）
    └── 00-core.yaml             # 核心概念（个体、关系、群体…）
```

**设计原则：**

- 每一条公理/推论/来源都是**独立文件**，方便 Git 追踪、引用、diff
- `candidates/` → `verified/` → `rejected/` 的生命周期用**目录移动**表示（而非状态字段），Git 天然记录轨迹
- 迭代快照提供"回退到上一个收敛点"的能力

---

## 3. 数据模型

### 3.1 数据流总览

```
来源层 (三大来源分别抽取规律主张)
  │
  ├──(支撑)──▶ 公理候选 ──(交叉验证)──▶ verified / rejected
  │                 ▲
  │                 │
  └──(投票)──▶ 交叉验证记录 (三来源各自 vote: agree | disagree | uncertain)
                    │
                    │ disagree → 一票否决 → contested → 矛盾调查 → 修正或否决
                    │
                    ▼ (verified 公理)
              推论层
              ├── 定理 (多步推导，可引用多条公理)
              └── 推论 (必须有现实锚点 + 可证伪条件)
```

### 3.2 基础概念定义 (`glossary/*.yaml`)

```yaml
# glossary/00-core.yaml
concepts:
  human_individual:
    definition: "具有自我意识和目标导向行动能力的智人个体"
    properties: [有限理性, 有偏好, 可感知环境, 可行动]
    notes: "暂不涉及自由意志辩论；采用方法论个体主义作为起点"

  social_relation:
    definition: "两个及以上个体之间持续存在的互动模式"
    subtypes: [kinship, exchange, authority, alliance, hostility]
    properties: [可重复, 可预期, 双向或单向]

  group:
    definition: "具有共同身份认同和内部互动规则的多成员集合"
    properties: [边界, 成员身份, 内部规范, 集体行动能力]
```

### 3.3 公理候选 (`axioms/candidates/AX-NNN.yaml`)

```yaml
id: AX-001
status: candidate          # candidate | verified | rejected
statement: |
  任何人类个体都具有有限理性：
  (a) 无法穷尽所有可能选项；
  (b) 无法精确计算每种选项的后果；
  (c) 在约束条件下追求满意解而非最优解。

domain: [个体行为]          # 适用领域标签
type: descriptive           # descriptive（实然）| normative（应然）

source_anchors:             # 每条公理至少一个来源锚点
  - source_id: EV-evo-001
    support: strong         # strong | moderate | weak
    quote: ""
  - source_id: EV-gt-001
    support: strong
    quote: ""

cross_verification:
  votes:
    evolutionary_biology: agree
    game_theory: agree
    cultural_universals: uncertain
  sources_agreeing: 2
  sources_conflicting: 0
  verdict: verified         # verified | contested | rejected
  verification_note: "演化生物学和博弈论高度一致；文化普适性来源待补充"

depends_on: []              # 引用的其他公理 ID
conflicts_with: []

created: 2026-07-13
iterations: [iter-001]
rejection_reason: null
```

### 3.4 来源证据 (`sources/<discipline>/EV-XXX.yaml`)

```yaml
id: EV-evo-001
discipline: evolutionary-biology
topic: "觅食决策的启发式策略"
claim: |
  在信息不完备和计算成本约束下，自然选择倾向于演化出简单启发式规则
  而非完整最优解搜索算法。

evidence_type: empirical    # empirical | theoretical | meta_analysis
strength: strong            # strong | moderate | suggestive

references:
  - "Gigerenzer, G. (2008). Rationality for Mortals."

supports_candidates: [AX-001]
```

### 3.5 交叉验证记录 (`sources/cross-verification/XV-NNN.yaml`)

```yaml
id: XV-001
target_axiom: AX-001
date: 2026-07-13

verdict: verified           # verified | contested | insufficient

votes:
  evolutionary_biology:
    status: agree
    evidence: [EV-evo-001]
    note: "有限理性在觅食行为中有大量实证"
  game_theory:
    status: agree
    evidence: [EV-gt-001]
    note: "Simon 的 bounded rationality 是博弈论的标准前提"
  cultural_universals:
    status: uncertain
    evidence: []
    note: "跨文化数据中'满意解'的行为模式普遍但未被系统性标记"

resolution: |
  2 agree + 1 uncertain → verified

# 当出现 disagree 时追加：
conflict_investigation:     # 仅当有 disagree 时填写
  disagree_source: game_theory
  disagree_reason: ""
  possible_resolutions:
    - "公理表述需要加限定条件"
    - "公理本身错误，应否决"
    - "该 disagree 来源的论证有漏洞"
  resolution_chosen: null
```

### 3.6 交叉验证阈值规则

**disagree 拥有一票否决权。** 无论其他几票 agree，出现 ≥1 disagree 即为 contested，必须启动矛盾调查。

| 投票分布 | 结论 |
|---|---|
| 3 agree | ✅ verified |
| 2 agree + 1 uncertain | ✅ verified |
| 1 agree + 2 uncertain | ⚠️ contested — 证据不足 |
| 出现 ≥1 disagree | ❌ contested — 一票否决，必须矛盾调查 |

### 3.7 定理 (`deductions/theorems/TH-NNN.yaml`)

```yaml
id: TH-001
statement: |
  在重复互动条件下，有限理性个体之间会自发形成简化规则
  以减少每次决策的计算成本。

depends_on:
  axioms: [AX-001]           # 有限理性
  prior_theorems: []

derivation:
  step_1: "有限理性 → 个体寻求降低决策成本 (AX-001)"
  step_2: "重复互动提供学习机会：过去互动结果可复用"
  step_3: "将过去互动模式固化为规则 → 未来同样情境无需重新计算"
  step_4: "→ 简化规则（惯例/规范）自发涌现"

corollaries: [CO-001, CO-002]
```

### 3.8 推论 (`deductions/corollaries/CO-NNN.yaml`)

```yaml
id: CO-001
derived_from:
  theorem: TH-001
  direct_from_axiom: false

statement: |
  任何长期存在的群体都会产生内部惯例，
  且惯例数量随群体存在时间递增。

real_world_anchors:
  - phenomenon: "任何公司运行几年后都有大量不成文规则"
    type: observation
    confidence: high
  - phenomenon: "原始部落的口传习俗体系"
    type: anthropological_record
    confidence: high

verification:
  status: verified           # verified | falsified | untested
  falsifiability: "若发现一个存在超过 N 年的群体完全无惯例，则推论被证伪"
```

### 3.9 迭代快照 (`iterations/iter-NNN/snapshot.yaml`)

```yaml
iteration: 1
date: 2026-07-13
status: converged            # converging | converged | diverging

axioms:
  verified: [AX-001, AX-003, AX-007]
  contested: [AX-004, AX-009]
  rejected: [AX-002, AX-005]

theorems: [TH-001]
corollaries: [CO-001, CO-002]

stats:
  total_axiom_candidates: 9
  verified_rate: 0.33
  cross_source_agreement: 0.78
  coverage_gaps:
    - "权力/支配关系的起源"
    - "群体间冲突的动力学"

glossary_terms_defined: 12
```

---

## 4. 迭代工作流

### 4.1 五阶段周期

```
iter-NNN 开始
  │
  ├── S1 扫源 ── 从三学科中提取新的规律主张
  │    产出: sources/<discipline>/EV-*.yaml
  │
  ├── S2 提炼候选公理 ── 把来源主张抽象为公理候选
  │    产出: axioms/candidates/AX-*.yaml
  │
  ├── S3 交叉验证 ── 三来源各自独立投票
  │    ├── disagree → 矛盾调查 → 修正或否决
  │    产出: sources/cross-verification/XV-*.yaml
  │    通过 → axioms/verified/
  │    否决 → axioms/rejected/
  │
  ├── S4 推导 ── 从已验证公理推导定理/推论
  │    产出: deductions/theorems/TH-*.yaml
  │          deductions/corollaries/CO-*.yaml
  │    每个推论必须挂现实锚点
  │
  └── S5 收敛判断
       产出: snapshot.yaml + CONCLUSION.md + diff.yaml
```

### 4.2 收敛条件（三个全满足才算收敛）

1. 本轮无新增 verified 公理（候选池已干涸或全部 contested）
2. 本轮无推论被现实锚点证伪
3. 公理之间无新发现的冲突

### 4.3 下一轮触发条件（满足任一即启动）

- 新增来源材料（新论文、新数据）
- 发现了上一轮"已知的未知"的答案
- 上一轮 contested 的矛盾调查有了新结论

### 4.4 阶段输出：CONCLUSION.md

```markdown
# 迭代 #001 阶段性结论

## 本轮成果
- 验证公理: 5 条 (AX-001, AX-003, AX-004, AX-007, AX-009)
- 定理: 2 条 (TH-001, TH-002)
- 推论: 4 条 (CO-001 ~ CO-004)，全部有现实锚点，未被证伪

## 已知的未知
- 权力/支配关系的起源尚无公理覆盖
- AX-006 被博弈论一票否决，矛盾待解
- 文化普适性来源对多条公理给出 "uncertain"

## 下一轮建议
- 优先补充人类学文献解决 uncertain 问题
- 对 AX-006 启动矛盾调查
```

---

## 5. 核心设计原则

1. **可追溯**：每条公理必须可追溯到来源证据；每个推论必须可追溯到定理/公理
2. **可证伪**：每个推论必须有明确的可证伪条件
3. **可回退**：迭代快照支持回退到任意历史收敛点
4. **独立性**：每条公理/推论是独立 YAML 文件，Git 可 diff
5. **disagree 一票否决**：不搞多数表决，一条命题要叫"公理"必须经得起所有来源的独立检验
6. **公开不完备**：每个 CONCLUSION.md 明确列出当前体系中无法解释的现象

---

## 6. 技术路线

- **第一阶段**：纯 YAML 迭代（当前），聚焦内容质量，不引入技术复杂度
- **第二阶段**：内容收敛后，编写脚本做一致性校验（公理间矛盾检测、推论回溯链路完整性、来源覆盖率统计）
- **第三阶段**：导入知识图谱数据库（SQLite / Neo4j），支持可视化查询
