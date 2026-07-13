# iter-001 Implementation Plan v2 — 人类社会公理化体系

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **v1 → v2 变更**：研究任务从"预填内容"改为"引导式探索"。基础设施任务保留预填。研究任务仅提供 YAML 模板 + 方法论指引 + 评价标准——内容由研究者（黄谦敏）在执行中产生，Claude 辅助记录、形式化、校验。
>
> **重要**：Tasks 4-9 是研究 workshop，不是抄写作业。这些任务之间允许且鼓励回退修改——发现后面的洞察后回去修正前面的公理是正常的研究行为，不是 plan 失败。

**Goal:** 完成 iter-001 完整研究周期：从基础设施搭建 → L0 概念探索 → L0 公理确立 → 来源证据收集 → L1 桥接验证 → 推论推导 → 迭代快照。

**Architecture:** 双层架构 (L0 定义层 + L1 桥接层)。L0 通过对抗式 negation_test 确立，L1 通过多来源 IEA 加权验证。所有实体为独立 YAML 文件。

**Tech Stack:** Python 3 (PyYAML 校验)，YAML (数据载体)，Git (版本控制)

**研究哲学:** Plan 提供结构和模板，不提供答案。研究者做判断，Claude 做记录和校验。

## Global Constraints

- 所有 YAML 文件使用 `.yaml` 后缀
- 文件 ID 格式：L0 公理 `AX-L0-NNN`，L1 桥接 `BR-L1-NNN`，来源证据 `EV-<discipline>-NNN`
- 所有实体文件保持固定路径，状态用 `status` 字段
- 每个推论必须有 `falsifiability` 和 `falsification_trace`
- 锚点 confidence 不能高于其 `source_type` 级别
- L0 公理必须通过对抗式 negation_test
- L1 桥接必须经过多来源 IEA 验证

---

## Phase A: 基础设施（可直接执行）

### Task 1: 项目基础设施搭建

**Files:**
- Create: `META.yaml`
- Create: `README.md`
- Create: `L0-definitions/contested/.gitkeep`
- Create: `L1-bridging/candidates/.gitkeep`
- Create: `L1-bridging/verified/.gitkeep`
- Create: `L1-bridging/weakly_verified/.gitkeep`
- Create: `L1-bridging/rejected/.gitkeep`

- [ ] **Step 1: 创建 META.yaml**

```yaml
# META.yaml — 项目哲学声明
project: human-society-axiomatics
version: 3.0
architecture: L0-L1-double-layer

epistemology:
  completeness_claim: "阶段性"
  known_limits:
    - 哥德尔不完备性
    - 涌现不可约性
    - 观察者偏误
    - 历史偶然性
  iteration_purpose: >
    每一轮追求比上一轮更少矛盾、更广覆盖面、更精炼的公理集。
  execution_honesty: >
    本体系设计了制衡机制（对抗式辩论、多来源验证、IEA 加权），
    在单研究者执行时退化为自我检查。这不否定制衡机制的价值——
    它们强制记录判断过程。透明的记录 > 假装客观。

methodology:
  l0: 定义性公理，对抗式 negation_test。真值来自概念定义。
  l1: 桥接命题，多来源 IEA 加权验证。可被证伪和修正。
  sources: [evolutionary_biology, game_theory, cultural_universals]
  verification: iea_weighted_voting
  iteration: 5_phase_cycle

created: 2026-07-13
```

- [ ] **Step 2: 创建 README.md**

```markdown
# 人类社会公理化体系

基于公理，推出推论。研究对象：人类社会。

## 方法论

双层架构：
- **L0 定义层**：从概念定义出发，形式化演绎。分析性真理。
- **L1 桥接层**：将 L0 连接到真实人类社会。多来源 IEA 加权验证。

本体系**永远不完备**。每一轮迭代产出阶段性结论。

## 快速开始

```bash
python scripts/validate.py                    # 一致性校验
cat iterations/iter-001/CONCLUSION.md         # 最新阶段性结论
```

## 目录

```
L0-definitions/   # 定义层（不需验证）
L1-bridging/      # 桥接层（需验证）
deductions/       # 推论层
sources/          # 多来源证据
iterations/       # 迭代快照
```

## 设计文档

[docs/design/2026-07-13-human-society-axiomatics-design.md](docs/design/2026-07-13-human-society-axiomatics-design.md)
```

- [ ] **Step 3: 创建空目录占位文件**

```bash
touch L0-definitions/contested/.gitkeep
touch L1-bridging/candidates/.gitkeep
touch L1-bridging/verified/.gitkeep
touch L1-bridging/weakly_verified/.gitkeep
touch L1-bridging/rejected/.gitkeep
```

- [ ] **Step 4: 提交**

```bash
git add META.yaml README.md L0-definitions/contested/.gitkeep L1-bridging/*/.gitkeep
git commit -m "feat: project scaffolding — META, README, directories"
```

---

### Task 2: 来源独立性模型

**Files:**
- Create: `sources/independence-model.yaml`

- [ ] **Step 1: 创建 independence-model.yaml**

```yaml
# sources/independence-model.yaml
# 多来源独立性模型 — 用于 IEA（独立 agree 当量）计算
#
# independence: 1.0 = 完全独立, 0.0 = 完全重叠
#
# 重要限制：
#   独立性系数随命题变化。此处为启发式默认值。
#   特定命题的交叉验证记录可覆盖默认值。
#   这些系数的作用是让独立性风险可见，不是提供精密量化。

version: 1
created: 2026-07-13

source_pairs:
  evo_bio__game_theory:
    independence: 0.4
    overlap_domains:
      - "evolutionary game theory (ESS, replicator dynamics)"
      - "cooperation evolution (kin selection ↔ repeated PD)"
      - "signaling theory"
    note: "核心数学结构共享。在'合作演化'和'信号传递'上几乎是一棵树。"

  evo_bio__cultural_universals:
    independence: 0.6
    overlap_domains:
      - "evolutionary psychology (跨文化验证演化假说)"
      - "human behavioral ecology"
    note: "evo 提供理论框架，cultural 提供跨文化数据。方法论路径不同。"

  game_theory__cultural_universals:
    independence: 0.5
    overlap_domains:
      - "跨文化行为实验 (ultimatum game, public goods game)"
      - "跨文化合作与惩罚研究 (Henrich et al.)"
    note: "gt 提供实验范式，cultural 提供跨文化样本。"

default_independence: 0.6

calibration_note: >
  初始估计值。随验证经验积累校准。当前 v1 系数在 ±0.2 范围内
  有启发性意义，不宜过度解读小数差异。
```

- [ ] **Step 2: 提交**

```bash
git add sources/independence-model.yaml
git commit -m "feat: independence model — evo↔gt(0.4) evo↔cu(0.6) gt↔cu(0.5)"
```

---

### Task 3: 最小校验脚本

**Files:**
- Create: `scripts/validate.py`
- Create: `requirements.txt`

**约束：** 只做最基础的检查——在实体积累到一定数量后再根据实际痛点扩展。不提前过度设计。

- [ ] **Step 1: 创建 requirements.txt**

```
PyYAML>=6.0
```

- [ ] **Step 2: 创建 validate.py（最小版本）**

```python
#!/usr/bin/env python3
"""validate.py — 一致性校验（最小版本，随使用扩展）"""

import os, sys, yaml
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"iterations", ".git", "__pycache__", "docs"}


def load_entities():
    """加载所有 YAML 实体"""
    entities = {}
    for yf in PROJECT_ROOT.rglob("*.yaml"):
        if any(d in yf.parts for d in SKIP_DIRS):
            continue
        if yf.name == "independence-model.yaml" or yf.name == "META.yaml":
            continue
        try:
            with open(yf) as f:
                data = yaml.safe_load(f)
            if data and isinstance(data, dict) and "id" in data:
                entities[str(yf.relative_to(PROJECT_ROOT))] = data
        except yaml.YAMLError as e:
            print(f"❌ YAML 错误: {yf.relative_to(PROJECT_ROOT)}: {e}")
    return entities


def check_id_uniqueness(entities):
    """ID 不能重复"""
    id_map = defaultdict(list)
    for path, e in entities.items():
        id_map[e["id"]].append(path)
    errors = []
    for eid, paths in id_map.items():
        if len(paths) > 1:
            errors.append(f"ID 重复: '{eid}' -> {paths}")
    if errors:
        for e in errors: print(f"❌ {e}")
    else:
        print(f"✅ ID 唯一性: {len(entities)} 个实体无重复")
    return errors


def check_references(entities):
    """引用的 ID 必须存在"""
    all_ids = set(e["id"] for e in entities.values())
    errors = []
    for path, e in entities.items():
        eid = e.get("id", "?")
        # 遍历所有字段递归找 ID 引用
        def check_refs(obj, ctx=""):
            if isinstance(obj, str) and obj in all_ids:
                pass  # 找到了就 OK
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    # 各种引用字段
                    if k in ("bridges_to_concept", "target_bridging",
                             "source_id", "primary_suspect", "secondary_suspect",
                             "unlikely_suspect"):
                        if isinstance(v, str) and v and v not in all_ids:
                            errors.append(f"{eid}: {k}='{v}' 不存在")
                    elif k in ("depends_on_l0", "supports_bridging",
                               "conflicts_with", "l0_axioms", "l1_bridging"):
                        if isinstance(v, list):
                            for ref in v:
                                if isinstance(ref, str) and ref not in all_ids:
                                    errors.append(f"{eid}: {k} 引用 '{ref}' 不存在")
                    check_refs(v, f"{ctx}.{k}")
            elif isinstance(obj, list):
                for item in obj:
                    check_refs(item, ctx)
        check_refs(e)

    if errors:
        for e in errors: print(f"❌ {e}")
    else:
        print("✅ 引用完整性: 通过")
    return errors


def check_status(entities):
    """简单状态检查"""
    errors = []
    for path, e in entities.items():
        eid = e.get("id", "?")
        # 推论必须有 falsification_trace
        if "deductions/corollaries" in path:
            ft = e.get("falsification_trace")
            if not ft or "primary_suspect" not in (ft or {}):
                errors.append(f"{eid}: 推论缺少 falsification_trace.primary_suspect")
            if not e.get("real_world_anchors"):
                errors.append(f"{eid}: 推论缺少 real_world_anchors")
        # L0 公理必须有 negation_test
        if "L0-definitions/axioms" in path:
            nt = e.get("negation_test")
            if not nt:
                errors.append(f"{eid}: L0 公理缺少 negation_test")
            elif nt.get("verdict") not in ("passes", "fails", "contested"):
                errors.append(f"{eid}: negation_test.verdict 无效值")
        # L1 桥接必须有 cross_verification
        if "L1-bridging" in path and e.get("status") == "verified":
            cv = e.get("cross_verification")
            if not cv:
                errors.append(f"{eid}: verified 桥接缺少 cross_verification")
            iea = cv.get("iea")
            if iea is not None and iea < 1.2:
                errors.append(f"{eid}: IEA={iea} 但状态为 verified (需 ≥1.2)")

    if errors:
        for e in errors: print(f"❌ {e}")
    else:
        print("✅ 状态检查: 通过")
    return errors


def main():
    print("=" * 50)
    print("一致性校验")
    print("=" * 50)

    entities = load_entities()
    if not entities:
        print("\n尚无实体文件。校验完成。")
        return

    print(f"\n加载 {len(entities)} 个实体\n")

    all_errors = []
    all_errors.extend(check_id_uniqueness(entities))
    all_errors.extend(check_references(entities))
    all_errors.extend(check_status(entities))

    print(f"\n{'='*50}")
    if all_errors:
        print(f"❌ {len(all_errors)} 个错误")
        sys.exit(1)
    else:
        print("✅ 全部通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 验证能运行**

```bash
pip install PyYAML
python scripts/validate.py
# 预期: "尚无实体文件。校验完成。"
```

- [ ] **Step 4: 提交**

```bash
git add scripts/validate.py requirements.txt
git commit -m "feat: validate.py — 最小一致性校验 (ID+引用+状态)"
```

---

## Phase B: 研究 Workshop（引导式探索）

以下每个任务是一次**研究 session**。Claude 的角色是：

1. 提供 YAML 模板和研究方法论指引
2. 就研究者的初步想法提出追问和 sharpening 的问题
3. 将研究者的判断形式化为 YAML 文件
4. 运行 validate.py 确保一致性
5. 如果后续任务发现需要回修前面的内容 → 这是在 plan 范围内的正常行为，直接做

**螺旋原则**：Task N 的发现可以触发对 Task M（M<N）的回修。这不是 plan 失败——这是研究的自然过程。回修后重新运行 validate.py 并提交。

---

### Task 4: L0 核心概念 Workshop

**目标**：定义 3-5 个讨论"人类社会"时不可绕过的分析原语。

**产出目录**：`L0-definitions/concepts/CONCEPT-*.yaml`

**方法论指引**：

概念是 L0 的基础。选择标准：
- 它是讨论人类社会时无法绕过的原语——不用它就无法讨论社会现象
- 它不是经验命题——你不需要"研究"来知道它的含义，它是你分析社会的**工具**
- 它足够抽象——不预设特定的社会形态或历史阶段

**模板** (`L0-definitions/concepts/CONCEPT-<name>.yaml`)：

```yaml
id: CONCEPT-<name>
term: "<中文名> (<English>)"
definition: |
  <精确的定义。包含必要特征。格式：(a)...(b)...(c)...>

logical_implications:
  - "<从定义中必然推出的逻辑蕴含 1>"
  - "<从定义中必然推出的逻辑蕴含 2>"
  - "<从定义中必然推出的逻辑蕴含 3>"

domain: [基础概念]
created: 2026-07-13
```

**引导问题**（Claude 在 workshop 中逐一提问）：

1. "如果要讨论人类社会，你第一时间想到的最基本的分析单元是什么？——人？关系？群体？制度？行动？"
2. "这个概念的**必要特征**是什么？缺了哪一个特征这个概念就不再是它？"
3. "从这个定义，你能直接推出什么？——不引入任何经验知识的情况下。"
4. "有没有一个更基础的概念，当前这个概念依赖它？——如果有，那个概念应该先定义。"
5. "这个概念的定义中，有没有隐含任何关于'人类实际上怎么样'的假设？——如果有，那个部分不属于 L0，应该留在 L1。"

**评价标准**：
- ✅ 定义中不含经验假设（"人类是 XXX" → 属于 L1）
- ✅ 否定定义会导致概念崩溃（为 negation_test 做准备）
- ✅ logical_implications 真正从定义中必然推出

**每完成一个概念 → 提交。**

---

### Task 5: L0 定义公理 Workshop

**目标**：从概念定义中提取公理，并通过对抗式否定检验。

**产出目录**：`L0-definitions/axioms/AX-L0-NNN.yaml`

**方法论指引**：

公理来自概念的 logical_implications 和跨概念的联系。选择标准：
- 它断言了两个以上概念之间的**结构性关系**（不只是单一概念的同义反复）
- 否定它将导致至少一个概念崩溃
- 它不引入任何经验内容

**模板** (`L0-definitions/axioms/AX-L0-NNN.yaml`)：

```yaml
id: AX-L0-NNN
statement: |
  <一句公理的完整表述>

type: definitional_axiom

derived_from_concepts:
  - <CONCEPT-xxx>: |
      <引用该概念的相关定义部分，展示此公理的来源>

negation_test:
  proposer_argument: |
    <正面论证：为什么否定它会导致概念崩溃>

  challenger_argument: |
    <对抗式反驳——认真地、有力地质疑 proposer 的论证>
    <Challenger 的目标不是走过场。要找出真正的弱点。>

  proposer_rebuttal: |
    <对 challenger 的回应——接受有效批评，驳斥无效批评>

  verdict: <passes | fails | contested>
  verdict_rationale: |
    <为什么做这个判决>

  unresolved: <true | false>
  contested_by: []
  date: 2026-07-13
```

**引导问题**（Claude 逐一提问）：

1. "从已有的概念定义中，哪些 logical_implications 跨越了两个以上的概念？"
2. "这条公理如果被否定，哪个概念会崩溃？——精确指出是哪个概念、为什么。"
3. "现在我是 challenger：请认真听听我的反驳。你需要回应它，或者承认它揭示了一个问题。"
4. "这条公理有没有引入经验假设？——'群体有边界' 是定义性的，但 '人类群体有边界' 是经验性的。确保你的公理是前者。"

**每完成一条公理（含完整的 negation_test）→ 提交。**
**如果 negation_test 的结果挑战了某个概念定义 → 回到 Task 4 修改。**

---

### Task 6: 来源证据收集 Workshop

**目标**：从三个学科中提取可靠的规律主张，为 L1 桥接提供锚点。

**产出目录**：`sources/<discipline>/EV-<discipline>-NNN.yaml`

**方法论指引**：

每条来源证据是一个关于人类社会的**可检验命题**，来自该学科中可靠的文献或理论。

选择标准：
- 有明确的文献支撑（可追溯到具体研究或理论）
- 表述为可检验的经验命题（不是纯哲学立场）
- 覆盖了未来 L1 桥接可能需要锚定的领域
- 优先选有实证支撑的，次选理论推导

**模板** (`sources/<discipline>/EV-<discipline>-NNN.yaml`)：

```yaml
id: EV-<discipline>-NNN
discipline: <evolutionary-biology | game_theory | cultural_universals>
topic: "<一句话描述主题>"
claim: |
  <该学科中对人类社会的一个具体、可检验的规律性主张>

evidence_type: <empirical | theoretical | meta_analysis>
strength: <strong | moderate | suggestive>

references:
  - "<Author (Year). Title. Venue.>"

supports_bridging: []          # 待 L1 桥接创建后回填
created: 2026-07-13
```

**引导问题**（Claude 逐一提问）：

1. "你想先从哪个学科开始？为什么？"
2. "这个学科中，最不争议的、关于人类社会的规律是什么？"
3. "这条规律在你的知识中是'自己知道的'还是'有具体文献来源的'？——如果是前者，我们需要标注为需要查证。"
4. "这条规律的证据类型是什么？——实证研究？理论推导？元分析？"
5. "这个学科还有哪些规律是未来的桥接命题可能需要的？——即使现在不写 L1，也可以先收集。"

**每个学科完成一批 → 提交。**
**可以在后续 Task 7-8 中发现需要补充新证据时回到这个 Task。**

---

### Task 7: L1 桥接 Workshop

**目标**：将 L0 的抽象概念连接到真实人类社会。写出桥接命题 + 执行多来源交叉验证。

**产出目录**：`L1-bridging/<candidates|verified|weakly_verified>/BR-L1-NNN.yaml`

**方法论指引**：

桥接命题 = "在人类社会中，L0 概念 X 呈现 Y 特征"。

关键约束：
- 每条桥接必须连接到至少一个 L0 概念
- 每条桥接必须标注哪些来源有领域资格（applicable_sources）
- 必须执行交叉验证——每个有资格的来源投票

**模板** (`L1-bridging/<status>/BR-L1-NNN.yaml`)：

```yaml
id: BR-L1-NNN
status: <candidate | verified | weakly_verified | rejected>

statement: |
  <关于真实人类社会的经验命题>

bridges_to_concept: <CONCEPT-xxx>
bridges_field: "<桥接的具体维度>"

applicable_sources:
  - <evolutionary-biology>
  - <game_theory>
  - <cultural_universals>
  # 只列有领域资格的来源。如 evo 不研究现代国家制度 → 不列。

source_anchors:
  - source_id: <EV-xxx-NNN>
    support: <strong | moderate | weak>
    note: "<为什么这个证据支持/不支持>"

cross_verification:
  votes:
    <discipline>:
      status: <agree | disagree | uncertain | not_applicable>
      weight: <来自 independence-model 的系数>
      evidence: [<EV-xxx-NNN>]
      note: "<投票理由>"
      independence_note: "<如有独立性风险，在此标注>"
    # ... 每个 applicable_source 一条
  iea: <Σ agree_source_weights>
  verdict: <verified | weakly_verified | contested | rejected>
  verdict_note: "<IEA 阈值判断 + 特殊考量>"

# 仅当有 disagree 时填写：
conflict_investigation:
  disagree_source: <discipline>
  disagree_reason: ""
  possible_resolutions:
    - ""
    - ""
  resolution_chosen: null

depends_on_l0: [<CONCEPT-xxx>]
conflicts_with: []
created: 2026-07-13
iterations: [iter-001]
```

**IEA 参考表**（执行时对照）：

| IEA | 结论 |
|---|---|
| IEA ≥ 1.8 | ✅ verified — 两个准独立来源 |
| 1.2 ≤ IEA < 1.8 | ✅ verified — 标注独立性风险 |
| 0.6 ≤ IEA < 1.2 | ⚠️ weakly_verified |
| IEA < 0.6 | ❌ contested |
| 出现 disagree | ❌ contested — 一票否决 |

**引导问题**（Claude 逐一提问）：

1. "L0 已经有了这些概念和公理。现在我们来看真实的人类社会——第一条经验桥梁应该架在哪里？"
2. "这个命题哪些来源有发言权？——博弈论能讨论'现代国家'吗？演化生物学能讨论'法律'吗？想清楚再列 applicable_sources。"
3. "现在为每个有资格的来源投票。对于每条证据——它支持还是反对还是不确定？"
4. "注意两个来源的独立性——如果 evo 和 gt 都 agree 但共享同一个理论源头，需要标注 independence_note。"
5. "计算 IEA。到了哪个阈值？"
6. "如果有 disagree——一票否决。这是真正的矛盾还是来源的领域边界问题？需要启动矛盾调查。"

**每完成一条桥接 → 提交。**
**如果交叉验证暴露了来源证据不足 → 回到 Task 6 补充。**
**如果桥接命题触及了某个 L0 公理的边界 → 回到 Task 5 修正。**

---

### Task 8: L0 定理 Workshop

**目标**：从 L0 公理和概念出发，进行纯定义演绎。

**产出目录**：`L0-definitions/theorems/TH-L0-NNN.yaml`

**方法论指引**：

L0 定理是纯逻辑演绎——从定义和公理推出必然结论，不引入经验。

**模板** (`L0-definitions/theorems/TH-L0-NNN.yaml`)：

```yaml
id: TH-L0-NNN
statement: |
  <必然推出的结论>

type: l0_theorem

derivation:
  from_axioms: [<AX-L0-NNN>]
  from_concepts: [<CONCEPT-xxx>]
  rule: <conjunction_introduction | modus_ponens | definitional_subsumption | ...>
  formal_steps:
    - "<步骤 1: 清楚展示推理的每一步>"
    - "<步骤 2>"
    - "<步骤 N>"
  note: "<为什么这个推导不需要经验——它只是让隐含的蕴含关系显式化>"
```

**关键约束**：
- 推导不能引入任何经验假设
- 每一步必须是逻辑变换或定义展开
- 如果一条定理需要"在人类社会中..."的限定 → 它不属于 L0，属于混合定理层

**引导问题**（Claude 逐一提问）：

1. "从 L0 公理集出发，哪些结论是必然的但尚未显式陈述？"
2. "这个推导中，有哪一步依赖了'常识'而非形式逻辑？——如果有，你需要用定义展开替代常识。"
3. "这条定理是否在任何可能世界都成立（只要概念定义相同）？——如果是，它是 L0 定理。如果只在人类真实社会中成立，它是混合定理。"

**每完成一条 → 提交。**
**如果推导暴露了公理表述不够精确 → 回到 Task 5 修正。**

---

### Task 9: 混合定理 + 推论 Workshop

**目标**：L0 × L1 → 关于真实社会的推论。

**产出目录**：`deductions/theorems/TH-NNN.yaml` + `deductions/corollaries/CO-NNN.yaml`

**方法论指引**：

混合定理 = L0 演绎结构 × L1 经验桥接。推论 = 混合定理的直接可检验产物。

**混合定理模板** (`deductions/theorems/TH-NNN.yaml`)：

```yaml
id: TH-NNN
statement: |
  <L0 结构 + L1 经验 → 关于人类社会的定理>

type: hybrid_theorem

depends_on:
  l0: [<AX-L0-NNN>, <TH-L0-NNN>]
  l1: [<BR-L1-NNN>]

derivation:
  type: empirical_inference
  evidence_weight: <very_strong | strong | moderate | suggestive>
  steps:
    - "L0: <l0 结构的贡献>"
    - "L1: <l1 桥接的贡献 (标注 IEA)>"
    - "⇒ <合成结论>"
  note: "<推导的置信度取决于 L1 桥接的 IEA 和推导强度>"

corollaries: [<CO-NNN>]
confidence: <very_high | high | moderate | low>
  # 综合判断：min(L1 bridge IEA) + 推导强度
```

**推论模板** (`deductions/corollaries/CO-NNN.yaml`)：

```yaml
id: CO-NNN
statement: |
  <可直接与现实对照的具体命题>

derived_from:
  theorem: <TH-NNN>
  l0_axioms: [<AX-L0-NNN>]
  l1_bridging: [<BR-L1-NNN>]
  confidence: <very_high | high | moderate | low>

real_world_anchors:
  - phenomenon: "<具体的现实现象描述>"
    type: <observation | anthropological_record | historical_record | empirical_record>
    source_type: <systematic_review | meta_analysis | empirical_study | case_study | expert_opinion | personal_observation>
    confidence: <very_high | high | moderate | low>
    note: "<为什么选择这个锚点，它有什么局限>"

verification:
  status: <verified | falsified | untested>
  falsifiability: |
    <什么观察会证伪这条推论？越具体越好。>

falsification_trace:
  primary_suspect: <BR-L1-NNN>
  failure_mode: "<如果推论被证伪，这个桥接最可能以什么方式错了>"
  secondary_suspect: <BR-L1-NNN 或 null>
  failure_mode: "<替代失败模式>"
  unlikely_suspect: <AX-L0-NNN 或 null>
  failure_mode: "<L0 极少出错，但如果出错会是怎么错的>"
```

**引导问题**（Claude 逐一提问）：

1. "从 verified 桥接出发，结合 L0 结构，你能推出什么非平凡的结论？"
2. "这个推论在现实世界中有对应的现象吗？——举出至少一个具体的、可观察的例子。"
3. "什么证据会推翻这个推论？——写出来，越具体越好。"
4. "如果推论被证伪，最可能是哪个桥接错了？——这是追责路径的核心。L0 公理极少是问题根源。"
5. "锚点的 evidence 级别是什么？——personal_observation 只能支撑 moderate confidence。"

**每完成一对（定理 + 推论）→ 提交。**
**如果推论制作过程中发现桥接需要调整 → 回到 Task 7。**
**如果发现需要新的来源证据 → 回到 Task 6。**

---

### Task 10: iter-001 快照 + 阶段性结论

**目标**：当研究者判断本轮已收敛，制作迭代快照。

**产出目录**：`iterations/iter-001/`

**收敛自检（研究者自己判断，三个都满足才 snapshot）**：

1. 本轮你想表达的 L0 公理都写完了，且通过了 negation_test
2. 本轮你想验证的 L1 桥接都经过了交叉验证，contested 的问题至少有了下一步调查方向
3. 推论都挂了现实锚点，尚未被证伪

**产出文件**：

- [ ] **snapshot.yaml** — 全量统计快照

```yaml
iteration: 1
date: 2026-07-13
status: converged

l0:
  concepts_defined: [<列表>]
  axioms: [<列表>]
  axioms_contested: [<列表>]
  theorems: [<列表>]

l1:
  verified: [<列表>]
  weakly_verified: [<列表>]
  contested: [<列表>]
  rejected: [<列表>]

deductions:
  theorems: [<列表>]
  corollaries: [<列表>]

stats:
  total_yaml_files: <N>
  iea_distribution:
    high: <N>    # ≥1.8
    medium: <N>  # 1.2-1.8
    low: <N>     # 0.6-1.2
  coverage_gaps:
    - "<本轮未覆盖的重要领域>"
  independence_concerns: <N>
```

- [ ] **diff.yaml** — 首轮标记为 initial

```yaml
iteration: 1
diff_from: null
diff_type: initial
summary: "<一句话描述本轮建立了什么>"
```

- [ ] **CONCLUSION.md** — 阶段性结论（自由文本，必须包含"已知的未知"）

```markdown
# 迭代 #001 阶段性结论

## 本轮成果
（自由概述）

## IEA 分析
（哪些桥接验证得最好？哪些有独立性风险？）

## 方法论反思
（对抗式 negation_test 运作得怎么样？多来源验证学到了什么？）

## 已知的未知
（本轮框架无法解释的社会现象。这是 iter-002 的种子。）

## 下一轮建议
```

- [ ] **提交**

```bash
git add iterations/iter-001/
git commit -m "docs: iter-001 snapshot — <本轮核心成果的一句话总结>"
```

---

## 附录 A：螺旋回退指南

| 在 Task N 发现... | 回退到 Task M | 做什么 |
|---|---|---|
| 公理表述需要更精确的概念定义 | Task 4 | 修改 CONCEPT |
| L1 桥接触及了 L0 公理的边界 | Task 5 | 增加或修正 AX-L0 |
| 交叉验证发现来源证据不足 | Task 6 | 补充 EV |
| 推论发现桥接太强/太弱 | Task 7 | 调整 BR-L1 |
| 推导暴露公理逻辑不严密 | Task 5 | 修正 AX-L0 |
| 任何回退后 | Task 3 | `python scripts/validate.py` |

## 附录 B：Task 依赖关系（允许回退）

```
Task 1 (脚手架) ──▶ Task 2 (独立性) ──▶ Task 3 (校验脚本)
                                            │
              ┌─────────────────────────────┘
              ▼
         Task 4 (L0 概念) ◀──────────────┐
              │                          │
              ▼                          │ (回修)
         Task 5 (L0 公理) ◀────────────┐ │
              │                        │ │
              ▼                        │ │
         Task 6 (来源证据) ◀──────────┐ │ │
              │                      │ │ │
              ▼                      │ │ │
         Task 7 (L1 桥接) ──────────┘ │ │
              │                        │ │
              ▼                        │ │
         Task 8 (L0 定理) ───────────┘ │
              │                          │
              ▼                          │
         Task 9 (混合定理 + 推论) ───────┘
              │
              ▼
         Task 10 (快照)
```
