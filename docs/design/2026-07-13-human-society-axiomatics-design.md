# 人类社会公理化体系 — 项目设计文档 v3

> 状态: approved | 日期: 2026-07-13 | 迭代: iter-000 (设计阶段)
>
> v2 → v3 变更：(a) negation_test 从单人 pass/fail 改为对抗式论证记录；(b) 来源验证从"三来源独立投票"改为"多来源加权依赖网络"；(c) "三来源交叉验证"更名为"多来源验证"。

## 1. 项目概要

### 1.1 核心目标

基于公理，推出推论。研究对象：人类社会。

构建一套双层知识体系：

- **L0 定义层**：从概念定义出发，进行形式化演绎。真值来自定义本身（分析性真理），不需要经验验证。
- **L1 桥接层**：将 L0 的抽象结构连接到真实人类社会。需要多来源验证（演化生物学、博弈论、文化普适性），可以被证伪和修正。

**核心洞察**：数学公理不需要验证（它不声称关于世界的任何事情），经验命题做不到严格演绎。这个矛盾通过双层分离解决——L0 做演绎，L1 做验证。

### 1.2 认识论立场 (META)

本体系**永远不完备**，每一轮迭代产出的是阶段性结论，而非最终真理。

1. **哥德尔不完备性**：任何足够复杂的公理系统，必然存在无法从公理推出的真命题，或存在矛盾。人类社会 >> 皮亚诺算术。
2. **涌现不可约性**：宏观社会现象不完全由微观公理加总决定。
3. **观察者效应**：研究者在系统内部观察系统。文化预设、语言边界、时代局限构成认知天花板。
4. **历史偶然性**：路径依赖不在公理化解释范围内。

### 1.3 成功标准 (MVP)

- **L0 公理集收敛**：5-10 条定义性公理。每条通过对抗式否定检验，self-consistent。
- **L1 桥接集收敛**：10-30 条桥接命题。每条通过多来源验证，独立 agree 当量 (IEA) ≥ 1.2。disagree 问题全部解决或标记。
- **可验证推论**：从 L0×L1 乘积出发，推出非平凡推论，每条有现实锚点 + 可证伪条件 + 追责路径。

---

## 2. 双层架构

### 2.1 架构总览

```
┌──────────────────────────────────────────────────┐
│  L0 定义层（真公理）                                │
│  ────────────────                                 │
│  不需要经验验证。概念之间的逻辑关系。                  │
│  这里的命题是分析性真理——真值来自定义本身。           │
│                                                   │
│  例: "行动是有目的的行为"                            │
│  例: "若群体存在，则群体必有边界"                     │
│                                                   │
│  资格门槛：对抗式 negation_test 通过。               │
│  数量预期：5-10 条。                                │
└──────────────────────┬───────────────────────────┘
                       │ 桥接
┌──────────────────────▼───────────────────────────┐
│  L1 桥接层（经验命题）                              │
│  ────────────────                                 │
│  把 L0 的抽象结构连接到真实人类社会。                  │
│  需要多来源验证（加权依赖网络）。可被证伪和修正。        │
│                                                   │
│  例: "人类行动受到认知能力约束"                       │
│  例: "人类可以形成超越血缘的合作关系"                  │
│                                                   │
│  阈值：IEA ≥ 1.2 → verified                        │
│  数量预期：20-50 条。                               │
└──────────────────────┬───────────────────────────┘
                       │ L0 演绎 × L1 桥接
                       ▼
┌──────────────────────────────────────────────────┐
│  推论层                                           │
│  ────                                            │
│  推论 = L0 结构 × L1 桥接 → 关于现实世界的命题      │
│                                                   │
│  每个推论挂现实锚点 + 可证伪条件 + 追责路径。        │
│  若被证伪，沿 falsification_trace 回溯。            │
└──────────────────────────────────────────────────┘
```

### 2.2 L0 vs L1 对照

| | L0 定义公理 | L1 桥接命题 |
|---|---|---|
| **真值来源** | 定义本身（分析性真理） | 经验证据（综合真理） |
| **是否需要验证** | 否（对抗式论证） | 是，多来源加权验证 |
| **能否被证伪** | 否（只有有用/没用之分） | 是 |
| **被推翻时** | 废弃整个概念体系重建 | 修正或替换该命题 |
| **数量预期** | 5-10 条 | 20-50 条 |
| **资格门槛** | 对抗式 negation_test 通过 | IEA ≥ 1.2 |

### 2.3 L0 公理的资格标准：对抗式否定检验

一个命题要进入 L0，必须通过对抗式否定检验：**"否定它会导致概念崩溃"这一主张，必须经受对抗式质疑并存活。**

这承认了一个关键事实：negation_test 在边界案例上本质是一个哲学立场判断——无法算法化。但不否认这一点，而是**把判断过程透明化**——让争议本身成为可追溯的数据。

```yaml
# 对抗式否定检验记录
negation_test:
  proposer_argument: |
    "群体必有边界"——若无边界（成员/非成员区分），
    "群体"与"任意多人集合"无法区分。"群体"概念失效。

  challenger_argument: |       # 强制性反驳角色
    "边界可以是模糊的、渐变的、情境性的。
    一个'开放社群'仍然是一个有意义的群体概念，
    尽管其边界不清晰。概念不需要刚性定义。"

  proposer_rebuttal: |
    "模糊边界仍然是一种边界。即使边界是渐变的，
    存在'更内部'和'更外部'的梯度本身就预设了
    center-periphery 结构——这仍是一种边界。"

  verdict: passes               # passes | fails | contested
  verdict_rationale: |
    Challenger 的"边界可模糊"观察成立，但不构成
    对"群体需要边界"的否定——模糊 ≠ 无。
    Proposer rebuttal 击败了挑战。

  unresolved: false             # true → 进入 contested_L0
  contested_by: []
  date: 2026-07-13
```

**关键规则：**

- Challenger 角色是**强制性的**——不能一个人说了算。可用 LLM 扮演（"你是一位持怀疑态度的哲学家，请反驳以下命题..."）或真人审查。
- `contested` 是合法终态。如果 rebuttal 不能彻底击败 challenger，命题标记为 contested——仍可使用，但悬挂红旗，下一轮迭代重新审查。
- 判例积累。随着体系增长，过去 negation_test 的判例会形成自己的知识——你会知道什么类型的论证倾向于通过。

---

## 3. 来源独立性模型

### 3.1 问题陈述

演化生物学、博弈论、文化普适性不是三个独立来源。它们之间存在显著的交叉：

- 演化生物学 ↔ 博弈论：evolutionary game theory（ESS、replicator dynamics、kin selection ↔ repeated PD）
- 演化生物学 ↔ 文化普适性：进化心理学使用跨文化数据验证演化假说
- 博弈论 ↔ 文化普适性：跨文化行为实验（ultimatum game、public goods game 的全球研究）

"三来源独立投票"的隐含前提（三个独立证人）不成立。

### 3.2 解决方案：加权依赖网络

从"独立投票计票"变为"加权独立 agree 当量 (IEA) 计算"。

**来源依赖模型：**

```yaml
# sources/independence-model.yaml
source_pairs:
  evo_bio__game_theory:
    independence: 0.4          # 0 = 完全重叠，1 = 完全独立
    overlap_domains:
      - "evolutionary game theory (ESS, replicator dynamics)"
      - "cooperation evolution (kin selection ↔ repeated PD)"
    note: "核心数学结构共享。在'合作如何演化'上几乎是一棵树"

  evo_bio__cultural_universals:
    independence: 0.6
    overlap_domains:
      - "evolutionary psychology (跨文化验证演化假说)"
    note: "evo 提供理论，cultural 提供数据。各有独立方法论"

  game_theory__cultural_universals:
    independence: 0.5
    overlap_domains:
      - "跨文化行为实验 (ultimatum game, public goods game)"
    note: "gt 提供实验范式，cultural 提供跨文化样本"

default_independence: 0.6      # 未明确标注的命题对默认值（偏保守）
```

### 3.3 IEA 计算

```yaml
# 交叉验证记录
cross_verification:
  votes:
    evolutionary_biology:
      status: agree
      weight: 1.0                  # 基准权重始终为 1.0
    game_theory:
      status: agree
      weight: 0.4                  # 与 evo 独立性仅 0.4
      independence_note: "evo game theory 共享 ESS 数学框架"
    cultural_universals:
      status: uncertain
      weight: 0.6                  # uncertain 权重低，不贡献 agree 当量

  # IEA (独立 agree 当量) 计算：
  # agree 来源的权重和 = 1.0 + 0.4 = 1.4
  # uncertain 不贡献 agree 当量
  # disagree 的来源不参与 IEA 加总（触发一票否决流程）
  iea: 1.4
```

### 3.4 IEA 验证阈值

| IEA | 结论 |
|---|---|
| IEA ≥ 1.8 | ✅ verified — 至少两个准独立来源一致 |
| IEA ≥ 1.2 | ✅ verified |
| IEA ≥ 0.6 | ⚠️ weakly_verified — 实质接近单来源，标注风险 |
| IEA < 0.6 | ❌ contested — 证据不足以称为"多来源"验证 |

**disagree 规则不变**：有领域资格的 disagree 仍拥有一票否决权——无论 IEA 多少，出现 ≥1 disagree 即为 contested。

### 3.5 IEA 含义示例

**例 1：evo agree + gt agree（独立 0.4）**
- IEA = 1.0 + 0.4 = 1.4 → verified ⚠️
- 通过，但悬挂独立性风险——实质上是 1.4 个独立来源，不是 2 个。

**例 2：evo agree + cultural agree（独立 0.6）**
- IEA = 1.0 + 0.6 = 1.6 → verified
- 真正的交叉验证——方法论路径不同。

**例 3：仅 evo agree（无其他来源数据）**
- IEA = 1.0 → weakly_verified
- 诚实标注：这本质上是单来源证据，挂着红旗。

**例 4：evo agree + gt agree（独立 0.4）+ cultural agree（独立 0.6）**
- IEA = 1.0 + 0.4 + 0.6 = 2.0 → verified
- 看起来是 3 agree，但实际证据力 ≈ 2 个独立来源。好，但不是三倍好。

### 3.6 命名变更

~~"三来源交叉验证"~~ → **"多来源验证"**

理由：(a) 不暗示恰好三个；(b) 不暗示来源彼此独立；(c) 未来增加来源不需要改名称；(d) 去除"三条线必须凑齐"的心理负担——来源多样性 > 恰好三个。

---

## 4. 项目结构

```
research/human-society/
├── README.md
├── META.yaml
├── docs/design/
│
├── L0-definitions/                # 定义层（不需要经验验证）
│   ├── concepts/                  # 核心概念定义
│   │   └── CONCEPT-agent.yaml
│   ├── axioms/                    # 定义性公理（对抗式 negation_test）
│   │   └── AX-L0-001.yaml
│   ├── contested/                 # negation_test 未解决的争议公理
│   └── theorems/                  # L0 内部演绎出的定理
│       └── TH-L0-001.yaml
│
├── L1-bridging/                   # 桥接层（需要验证）
│   ├── candidates/                # 候选桥接命题
│   ├── verified/                  # IEA ≥ 1.2
│   ├── weakly_verified/           # 0.6 ≤ IEA < 1.2
│   └── rejected/                  # 被否决
│
├── deductions/                    # 推论层（L0 × L1 乘积）
│   ├── theorems/                  # 混合定理
│   └── corollaries/               # 推论 + 现实锚点 + 追责路径
│
├── sources/                       # 多来源证据
│   ├── independence-model.yaml    # 来源依赖模型 + 独立性系数
│   ├── evolutionary-biology/
│   ├── game-theory/
│   ├── cultural-universals/
│   └── cross-verification/        # 交叉验证记录（IEA 加权计票）
│
└── iterations/                    # 迭代快照
    └── iter-NNN/
        ├── snapshot.yaml
        ├── diff.yaml
        └── CONCLUSION.md
```

---

## 5. 数据模型

### 5.1 数据流总览

```
L0 定义层                            L1 桥接层
─────────                            ────────
概念定义 ──(逻辑蕴含)──▶ 定义公理        候选命题
    │              对抗式 negation_test     │
    │              passes/contested         ▼
    │                                   多来源加权验证
    │                                   IEA 计算 + disagree 否决
    │                                        │
    │                                   verified / weakly_verified
    │                                   / contested / rejected
    │                                        │
    └────────────────────────────────────────┘
                         │
                  L0 结构 × L1 桥接
                         │
                         ▼
                     推论层
                         │
                  现实锚点验证
                  证伪 → falsification_trace 回溯
```

### 5.2 概念定义 (`L0-definitions/concepts/CONCEPT-*.yaml`)

```yaml
id: CONCEPT-agent
term: "行动者 (Agent)"
definition: |
  一个具有目标导向行动能力的实体。
  必要特征：(a) 拥有目标/偏好；(b) 能感知环境状态；
  (c) 能执行改变环境状态的动作。

logical_implications:
  - "Agent 存在 ⇒ 目标存在"
  - "Agent 行动 ⇒ 环境状态改变"

domain: [基础概念]
created: 2026-07-13
```

### 5.3 L0 定义公理 (`L0-definitions/axioms/AX-L0-*.yaml`)

```yaml
id: AX-L0-001
statement: |
  若群体存在，则群体必有边界，
  边界定义了成员与非成员的区别。

type: definitional_axiom

derived_from_concepts:
  - CONCEPT-group: |
      "群体 = 具有共同身份认同和内部互动规则的多成员集合"
      其中"成员"预设了"非成员"的存在 ⇒ 边界是群体的逻辑必然。

# 对抗式否定检验（替代 v2 的 negation_test pass/fail）
negation_test:
  proposer_argument: |
    "群体必有边界"——若无边界（成员/非成员区分），
    "群体"与"任意多人集合"无法区分。"群体"概念失效。

  challenger_argument: |
    "边界可以是模糊的、渐变的、情境性的。
    一个'开放社群'仍然是一个有意义的群体概念，
    尽管其边界不清晰。概念不需要刚性定义才能工作。"

  proposer_rebuttal: |
    "模糊边界仍然是一种边界。即使边界是渐变的，
    存在'更内部'和'更外部'的梯度本身就预设了
    center-periphery 结构——这仍是一种边界。"

  verdict: passes               # passes | fails | contested
  verdict_rationale: |
    Challenger 的"边界可模糊"观察成立，但不构成对
    "群体需要边界"的否定——模糊 ≠ 无。
    Proposer rebuttal 击败了挑战。

  unresolved: false
  contested_by: []
  date: 2026-07-13

# L0 公理不需要 source_anchors 和 cross_verification
# 真值来自概念定义本身
```

### 5.4 来源证据 (`sources/<discipline>/EV-*.yaml`)

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

supports_bridging: [BR-L1-001]
```

### 5.5 L1 桥接命题 (`L1-bridging/*/BR-L1-*.yaml`)

```yaml
id: BR-L1-001
status: verified              # candidate | verified | weakly_verified | rejected

statement: |
  人类行动受到认知能力约束：
  (a) 无法穷尽所有可能选项；
  (b) 无法精确计算每种选项的后果；
  (c) 在约束条件下追求满意解而非最优解。

bridges_to_concept: CONCEPT-agent
bridges_field: "行动能力约束"

# 哪些来源对该命题有领域资格
applicable_sources:
  - evolutionary-biology
  - game_theory
  - cultural_universals

source_anchors:
  - source_id: EV-evo-001
    support: strong
  - source_id: EV-gt-001
    support: strong

cross_verification:
  votes:
    evolutionary_biology:
      status: agree
      weight: 1.0              # 基准权重
      evidence: [EV-evo-001]
    game_theory:
      status: agree
      weight: 0.4              # 与 evo 独立系数 0.4
      evidence: [EV-gt-001]
      independence_note: "bounded rationality 共享 Simon 理论源头"
    cultural_universals:
      status: uncertain
      weight: 0.6              # uncertain 不贡献 agree 当量
      evidence: []
  iea: 1.4                     # 独立 agree 当量
  verdict: verified            # IEA ≥ 1.2 → verified
  verdict_note: "IEA=1.4 通过但悬挂独立性风险——实质为 1.4 个独立来源"

depends_on_l0: [CONCEPT-agent]
conflicts_with: []

created: 2026-07-13
iterations: [iter-001]
rejection_reason: null
```

### 5.6 交叉验证记录 (`sources/cross-verification/XV-*.yaml`)

```yaml
id: XV-001
target_bridging: BR-L1-001
date: 2026-07-13

verdict: verified             # verified | weakly_verified | contested | insufficient

votes:
  evolutionary_biology:
    status: agree
    qualified: true
    evidence: [EV-evo-001]
    weight: 1.0
    note: "有限理性在觅食行为中有大量实证"
  game_theory:
    status: agree
    qualified: true
    evidence: [EV-gt-001]
    weight: 0.4
    note: "bounded rationality 是标准前提"
    independence_flag: "与 evo 共享 Simon 源头，独立系数 0.4"
  cultural_universals:
    status: uncertain
    qualified: true
    evidence: []
    weight: 0.6
    note: "满意解行为模式普遍但未被系统性标记"

iea: 1.4                       # Σ agree_source_weights
resolution: "IEA=1.4 ≥ 1.2 → verified。独立性风险已标注。"

# 仅当有 disagree 时填写：
conflict_investigation:
  disagree_source: null
  disagree_reason: ""
  possible_resolutions: []
  resolution_chosen: null
```

### 5.7 验证阈值规则 (v3)

**第一道关：disagree 一票否决。** 有领域资格的 disagree → contested，不管 IEA 多少。

**第二道关：IEA 加权阈值。**

| IEA | 结论 |
|---|---|
| IEA ≥ 1.8 | ✅ verified — 至少两个准独立来源一致 |
| 1.2 ≤ IEA < 1.8 | ✅ verified — 通过，标注独立性风险 |
| 0.6 ≤ IEA < 1.2 | ⚠️ weakly_verified — 实质近单来源 |
| IEA < 0.6 | ❌ contested — 不构成多来源验证 |

**来源资格规则：**

- 不在 `applicable_sources` 中的来源**不参与投票**（演化生物学不审议现代国家制度层面的命题）
- 同一来源的多条证据不叠加（一条 evo 证据 vs 三条 evo 证据，权重都是 1.0——IEA 衡量的是来源多样性，不是证据量）

### 5.8 L0 定理 (`L0-definitions/theorems/TH-L0-*.yaml`)

```yaml
id: TH-L0-001
statement: |
  若群体存在，则群体必有内部规范。

type: l0_theorem

derivation:
  from_axioms: [AX-L0-001]
  from_concepts: [CONCEPT-group]
  rule: conjunction_introduction
  formal_steps:
    - "AX-L0-001: 群体 ⇒ 有边界（成员资格）"
    - "CONCEPT-group: 群体定义包含'内部互动规则'"
    - "内部互动规则是规范的子类"
    - "⇒ 群体 ⇒ 存在内部规范"
  note: "这一步不需要经验。是 CONCEPT-group 定义的同义反复。"
```

### 5.9 L0×L1 定理 (`deductions/theorems/TH-*.yaml`)

```yaml
id: TH-001
statement: |
  在重复互动条件下，人类群体内部会自发涌现简化规则
  以减少每次决策的计算成本。

type: hybrid_theorem

depends_on:
  l0: [AX-L0-001, TH-L0-001]
  l1: [BR-L1-001]

derivation:
  type: empirical_inference
  evidence_weight: strong
  steps:
    - "L0: 群体 ⇒ 需内部规范 (TH-L0-001)"
    - "L1: 人类认知有限 (BR-L1-001, IEA=1.4)"
    - "⇒ 规范不能无限复杂 ⇒ 倾向于简化为惯例"
    - "⇒ 简化规则在重复互动中自发涌现"

corollaries: [CO-001, CO-002]
```

### 5.10 推论 (`deductions/corollaries/CO-*.yaml`)

```yaml
id: CO-001
statement: |
  任何长期存在的群体都会产生内部惯例，
  且惯例数量随群体存在时间递增。

derived_from:
  theorem: TH-001
  l0_axioms: [AX-L0-001, TH-L0-001]
  l1_bridging: [BR-L1-001]
  confidence: high              # 来自 L1 桥接的最小 IEA 和推导强度的综合

real_world_anchors:
  - phenomenon: "任何公司运行数年后都有大量不成文规则"
    type: observation
    source_type: personal_observation    # ← 锚点来源级别
    confidence: moderate                 # 不能超过来源级别
  - phenomenon: "原始部落的口传习俗体系"
    type: anthropological_record
    source_type: empirical_study
    confidence: high

# 锚点来源级别（confidence 不能高于来源级别）：
# systematic_review > meta_analysis > empirical_study
# > case_study > expert_opinion > personal_observation

verification:
  status: verified              # verified | falsified | untested
  falsifiability: "若发现存在超过 N 年的群体完全无内部惯例，则推论被证伪"

falsification_trace:
  primary_suspect: BR-L1-001    # 最可能出问题的 L1 桥接
  secondary_suspect: null
  unlikely_suspect: AX-L0-001   # L0 极少是问题根源
```

### 5.11 迭代快照 (`iterations/iter-NNN/snapshot.yaml`)

```yaml
iteration: 1
date: 2026-07-13
status: converged              # converging | converged | diverging

l0:
  concepts_defined: [CONCEPT-agent, CONCEPT-action, CONCEPT-relation, CONCEPT-group]
  axioms: [AX-L0-001, AX-L0-002]
  axioms_contested: []         # negation_test 未解决的
  theorems: [TH-L0-001]

l1:
  verified: [BR-L1-001, BR-L1-003, BR-L1-007]
  weakly_verified: [BR-L1-008] # IEA 不足
  contested: [BR-L1-004, BR-L1-009]
  rejected: [BR-L1-002, BR-L1-005]

deductions:
  theorems: [TH-001]
  corollaries: [CO-001, CO-002]

stats:
  l1_total_candidates: 9
  l1_verified_rate: 0.33       # verified / total
  iea_distribution:            # IEA 分布
    high: 2                     # IEA ≥ 1.8
    medium: 1                   # 1.2 ≤ IEA < 1.8
    low: 1                      # 0.6 ≤ IEA < 1.2
  coverage_gaps:
    - "权力/支配关系的起源"
    - "群体间冲突的动力学"
  independence_concerns: 2     # 标注了独立性 flag 的验证次数
```

---

## 6. 迭代工作流

### 6.1 五阶段周期 (v3)

```
iter-NNN 开始
  │
  ├── S1 扫源
  │    从多来源中提取规律主张
  │    产出: sources/<discipline>/EV-*.yaml
  │    维护: sources/independence-model.yaml
  │
  ├── S2 提炼
  │    ├── L0: 概念定义 → 定义公理 → 对抗式 negation_test
  │    │   challenger 强制反驳 → passes / contested
  │    │   产出: L0-definitions/concepts/* + axioms/* + contested/*
  │    │
  │    └── L1: 来源主张 → 桥接候选，标注 applicable_sources
  │        产出: L1-bridging/candidates/
  │
  ├── S3 多来源验证
  │    计算 IEA（独立 agree 当量）
  │    一票否决: disagree（有资格来源）→ contested
  │    IEA ≥ 1.2 → verified
  │    0.6 ≤ IEA < 1.2 → weakly_verified
  │    产出: sources/cross-verification/XV-*.yaml
  │
  ├── S4 推导
  │    L0 内部: 概念定义 → 严格演绎 → L0 定理
  │    混合层: L0 + L1 → 经验推断 → 定理 + 推论
  │    每个推论: 锚点 + 可证伪条件 + falsification_trace
  │    产出: deductions/theorems/* + deductions/corollaries/*
  │
  └── S5 收敛判断
       快照 snapshot.yaml + diff.yaml
       CONCLUSION.md（含已知的未知）
       若推论被证伪 → 沿 falsification_trace 回溯 → 标记可疑桥接
       → 触发下一轮重点审查
```

### 6.2 收敛条件

1. 本轮无新增 verified/weakly_verified 桥接命题
2. 本轮无推论被现实锚点证伪
3. L0 公理之间无新发现矛盾；L0 contested 列表无变化

### 6.3 触发条件

- 新增来源材料
- 上一轮"已知的未知"获得新证据
- 上一轮 contested 的矛盾调查有了新结论
- 推论被证伪 → 对该桥接启动重点审查

### 6.4 CONCLUSION.md

```markdown
# 迭代 #001 阶段性结论

## 本轮成果
- L0 概念: 4 个 | L0 公理: 2 条 | L0 contested: 0
- L1 verified: 3 条 (IEA 平均 1.5) | weakly_verified: 1 条 | contested: 2 条
- 混合定理: 2 条 | 推论: 4 条，全部未被证伪

## IEA 分布
- ≥1.8: 0 条 | ≥1.2: 3 条 | ≥0.6: 1 条
- 独立性风险标注: 2 次 (evo↔gt 重叠)

## 已知的未知
- 权力/支配关系的起源尚无公理或桥接覆盖
- BR-L1-006 被博弈论一票否决（disagree），矛盾待查
- 文化普适性来源对 3 条桥接投票 uncertain，人类学文献缺口

## 下一轮建议
- 补充人类学文献
- 对 BR-L1-006 启动矛盾调查
- 审查 independence-model.yaml 系数的合理性
```

---

## 7. 核心设计原则

1. **L0/L1 分层**：定义性公理和桥接命题物理隔离
2. **对抗式否定检验**：L0 不搞单人 pass/fail，强制 challenger 反驳，判例积累
3. **IEA 加权验证**：从"数票"变为"加权独立 agree 当量"
4. **独立审查**：来源依赖显式建模（independence-model.yaml）
5. **领域资格**：applicable_sources 限定投票权
6. **disagree 一票否决**：有领域资格的 disagree → contested，不管 IEA
7. **弱验证透明**：IEA < 1.2 → weakly_verified，不伪装成多来源共识
8. **可追溯**：桥接 → 来源证据；推论 → L0 + L1 + falsification_trace
9. **可证伪**：推论有明确可证伪条件 + 追责路径
10. **锚点分级**：confidence 不能超过来源级别
11. **可回退**：迭代快照支持回退到历史收敛点
12. **公开不完备**：CONCLUSION.md 列出无法解释的现象

---

## 8. 技术路线

- **第一阶段**：纯 YAML 迭代（当前），聚焦内容质量
- **第二阶段**：编写校验脚本 —— L0 矛盾检测、推论回溯链路完整性、IEA 分布报告、独立性风险热力图、锚点覆盖率
- **第三阶段**：导入知识图谱数据库（SQLite / Neo4j），可视化推导链和来源依赖网络

---

## 附录 A：版本变更追踪

| # | 问题 | v1 | v2 | v3 |
|---|---|---|---|---|
| 1 | 公理定位与验证矛盾 | 🔴 | L0/L1 双层架构 | 不变 |
| 2 | 候选资格未定义 | 🔴 | negation_test 门槛 | 对抗式 negation_test |
| 3 | 推导机制非形式化 | 🔴 | formal_steps + inference type | 不变 |
| 4 | 目录移动打断引用 | 🟡 | 固定路径 + status | 不变 |
| 5 | 来源独立性存疑 | 🟡 | independence_note 标注 | IEA 加权依赖网络 |
| 6 | disagree 忽略领域边界 | 🟡 | applicable_sources | 不变 |
| 7 | 锚点 confidence 无验证 | 🟢 | 锚点分级 | 不变 |
| 8 | 线性掩盖递归 | 🟢 | falsification_trace | 不变 |
| 9 | — | — | — | L0 negation_test 主观性 → 对抗式论证 |
| 10 | — | — | — | "三来源"→"多来源" + 独立系数显式建模 |
