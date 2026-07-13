# iter-001 研究指南 — 人类社会公理化体系

> **性质**：研究指南，不是施工蓝图。内容不预设，顺序不锁定，探索方向由研究者（黄谦敏）主导。Claude 的角色：提问、记录、形式化、校验。

**完成标准**（三个都满足就 snapshot）：
1. 你想表达的 L0 公理都写完了，通过 negation_test
2. L1 桥接通过了交叉验证，contested 的至少知道下一步调查方向
3. 推论有现实锚点，未被证伪

---

## Part 1: 一次性搭建

执行一次，3 个 commit，5 分钟。

### 脚手架

创建目录和项目声明文件。

```bash
# 目录（已存在则跳过）
mkdir -p L0-definitions/{concepts,axioms,contested,theorems}
mkdir -p L1-bridging/{candidates,verified,weakly_verified,rejected}
mkdir -p deductions/{theorems,corollaries}
mkdir -p sources/{evolutionary-biology,game-theory,cultural-universals,cross-verification}
mkdir -p iterations/iter-001

# 占位
touch L0-definitions/contested/.gitkeep
touch L1-bridging/{candidates,verified,weakly_verified,rejected}/.gitkeep
```

**META.yaml**：

```yaml
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
  execution_honesty: >
    制衡机制（对抗式辩论、多来源验证、IEA 加权）在单研究者执行时
    退化为自我检查。不否定其价值——它们强制记录判断过程。
    透明的记录 > 假装客观。

methodology:
  l0: 定义性公理，对抗式 negation_test。真值来自概念定义。
  l1: 桥接命题，多来源 IEA 加权验证。可证伪修正。
  sources: [evolutionary_biology, game_theory, cultural_universals]
  verification: iea_weighted_voting

created: 2026-07-13
```

**README.md**：

```markdown
# 人类社会公理化体系

基于公理，推出推论。研究对象：人类社会。

双层架构：L0 定义层（分析性真理）+ L1 桥接层（经验验证）。
本体系永远不完备。每一轮迭代产出阶段性结论。

设计文档: docs/design/2026-07-13-human-society-axiomatics-design.md

## 快速命令

python scripts/validate.py                 # 一致性校验
cat iterations/iter-001/CONCLUSION.md       # 最新阶段性结论
```

```bash
git add -A && git commit -m "feat: project scaffolding"
```

### 独立性模型

**`sources/independence-model.yaml`**：

```yaml
version: 1
created: 2026-07-13

source_pairs:
  evo_bio__game_theory:
    independence: 0.4
    overlap_domains:
      - "evolutionary game theory (ESS, replicator dynamics)"
      - "cooperation evolution (kin selection ↔ repeated PD)"
      - "signaling theory"
    note: "核心数学结构共享。在合作/信号主题上几乎是一棵树。"

  evo_bio__cultural_universals:
    independence: 0.6
    overlap_domains:
      - "evolutionary psychology (跨文化验证演化假说)"
      - "human behavioral ecology"
    note: "理论框架 vs 田野数据，方法论路径不同。"

  game_theory__cultural_universals:
    independence: 0.5
    overlap_domains:
      - "跨文化行为实验 (ultimatum game, public goods game)"
    note: "gt 提供范式，cu 提供样本。"

default_independence: 0.6

calibration_note: >
  初始估计值。v1 系数在 ±0.2 范围内有启发性意义，
  不宜过度解读小数差异。随验证经验校准。
```

```bash
git add sources/independence-model.yaml && git commit -m "feat: independence model"
```

### 校验脚本

**`scripts/validate.py`**（最小版本，随使用扩展）：

```python
#!/usr/bin/env python3
"""validate.py — 一致性校验"""
import sys, yaml
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"iterations", ".git", "__pycache__", "docs"}

def load():
    es = {}
    for f in ROOT.rglob("*.yaml"):
        if any(d in f.parts for d in SKIP): continue
        if f.name in ("independence-model.yaml", "META.yaml"): continue
        try:
            with open(f) as fh: d = yaml.safe_load(fh)
            if d and isinstance(d, dict) and "id" in d:
                es[str(f.relative_to(ROOT))] = d
        except yaml.YAMLError as e:
            print(f"❌ YAML: {f.relative_to(ROOT)}: {e}")
    return es

def check_ids(es):
    m = defaultdict(list)
    for p, e in es.items(): m[e["id"]].append(p)
    errs = [f"ID 重复: '{i}' -> {ps}" for i, ps in m.items() if len(ps) > 1]
    for e in errs: print(f"❌ {e}")
    print(f"✅ ID 唯一性: {len(es)} 实体" if not errs else "")
    return errs

def check_refs(es):
    ids = set(e["id"] for e in es.values())
    ref_fields = ["bridges_to_concept", "target_bridging", "source_id",
                  "primary_suspect", "secondary_suspect", "unlikely_suspect"]
    list_fields = ["depends_on_l0", "supports_bridging", "conflicts_with",
                   "l0_axioms", "l1_bridging"]
    errs = []
    for p, e in es.items():
        eid = e.get("id", "?")
        for k in ref_fields:
            v = e.get(k)
            if isinstance(v, str) and v and v not in ids:
                errs.append(f"{eid}: {k}='{v}' 不存在")
        for k in list_fields:
            for v in (e.get(k) or []):
                if isinstance(v, str) and v not in ids:
                    errs.append(f"{eid}: {k} 引用 '{v}' 不存在")
    for e in errs: print(f"❌ {e}")
    print("✅ 引用完整性: 通过" if not errs else "")
    return errs

def check_status(es):
    errs = []
    for p, e in es.items():
        eid = e.get("id", "?")
        if "deductions/corollaries" in p:
            if not e.get("falsification_trace", {}).get("primary_suspect"):
                errs.append(f"{eid}: 缺少 falsification_trace.primary_suspect")
            if not e.get("real_world_anchors"):
                errs.append(f"{eid}: 缺少 real_world_anchors")
        if "L0-definitions/axioms" in p:
            nt = e.get("negation_test", {})
            if nt.get("verdict") not in ("passes", "fails", "contested"):
                errs.append(f"{eid}: negation_test.verdict 缺失/无效")
        if "L1-bridging" in p and e.get("status") == "verified":
            cv = e.get("cross_verification", {})
            iea = cv.get("iea")
            if iea is not None and iea < 1.2:
                errs.append(f"{eid}: IEA={iea} 但状态为 verified (需 ≥1.2)")
    for e in errs: print(f"❌ {e}")
    print("✅ 状态检查: 通过" if not errs else "")
    return errs

def main():
    print("=" * 40 + "\n一致性校验\n" + "=" * 40)
    es = load()
    if not es: print("\n尚无实体。"); return
    print(f"\n{len(es)} 个实体\n")
    errs = check_ids(es) + check_refs(es) + check_status(es)
    print(f"\n{'='*40}")
    if errs: print(f"❌ {len(errs)} 个错误"); sys.exit(1)
    else: print("✅ 全部通过")

if __name__ == "__main__": main()
```

```bash
echo "PyYAML>=6.0" > requirements.txt
pip install PyYAML -q
python scripts/validate.py
# 预期: "尚无实体。"

git add scripts/validate.py requirements.txt
git commit -m "feat: validate.py — 最小校验"
```

---

## Part 2: 实体模板

以下模板按需查阅。研究时不需要按模板顺序填——先想清楚你要说什么，再用模板记录。

### L0 概念

```yaml
id: CONCEPT-<name>
term: "<中文名>"
definition: |
  <精确的定义。必要特征用 (a)(b)(c) 列出。>

logical_implications:
  - "<从定义必然推出的蕴含>"

domain: [基础概念]
created: 2026-07-13
```

**目录**：`L0-definitions/concepts/`

**门槛**：定义中不含经验假设。否定它会导致概念崩溃。

### L0 定义公理

```yaml
id: AX-L0-NNN
statement: |
  <公理表述>

type: definitional_axiom

derived_from_concepts:
  - <CONCEPT-xxx>: |
      <从该概念的哪部分定义推导出此公理>

negation_test:
  proposer_argument: |
    <正面论证>
  challenger_argument: |
    <认真反驳——找真正的弱点，不是走过场>
  proposer_rebuttal: |
    <回应挑战——接受有效批评，驳斥无效批评>
  verdict: <passes | fails | contested>
  verdict_rationale: |
    <判决理由>
  unresolved: <true | false>
  contested_by: []
  date: 2026-07-13
```

**目录**：`L0-definitions/axioms/`

**门槛**：通过对抗式 negation_test。Claude 扮演 challenger 时，会认真找你的论证弱点。

### 来源证据

```yaml
id: EV-<discipline>-NNN
discipline: <evolutionary-biology | game_theory | cultural_universals>
topic: "<一句话主题>"
claim: |
  <关于人类社会的可检验规律主张>

evidence_type: <empirical | theoretical | meta_analysis>
strength: <strong | moderate | suggestive>

references:
  - "<Author (Year). Title. Venue.>"

supports_bridging: []       # 桥接创建后回填
created: 2026-07-13
```

**目录**：`sources/<discipline>/`

**门槛**：有文献支撑，表述为可检验的经验命题。

### L1 桥接命题

```yaml
id: BR-L1-NNN
status: <candidate | verified | weakly_verified | rejected>

statement: |
  <关于真实人类社会的经验命题>

bridges_to_concept: <CONCEPT-xxx>
bridges_field: "<桥接的具体维度>"

applicable_sources:          # 只有有领域资格的列在这里
  - evolutionary-biology
  - game_theory
  - cultural_universals

source_anchors:
  - source_id: <EV-xxx>
    support: <strong | moderate | weak>
    note: ""

cross_verification:
  votes:
    <discipline>:
      status: <agree | disagree | uncertain | not_applicable>
      weight: <来自 independence-model 的系数>
      evidence: [<EV-xxx>]
      note: ""
      independence_note: ""   # 如有独立性风险
  iea: <Σ agree 来源的权重>
  verdict: <verified | weakly_verified | contested | rejected>
  verdict_note: ""

# 仅当有 disagree 时：
conflict_investigation:
  disagree_source: ""
  disagree_reason: ""
  possible_resolutions: []
  resolution_chosen: null

depends_on_l0: [<CONCEPT-xxx>]
conflicts_with: []
created: 2026-07-13
iterations: [iter-001]
```

**目录**：`L1-bridging/<status>/`

**IEA 阈值**：

| IEA | 结论 |
|---|---|
| ≥ 1.8 | ✅ verified — 两个准独立来源 |
| 1.2 ~ 1.8 | ✅ verified — 标注独立性风险 |
| 0.6 ~ 1.2 | ⚠️ weakly_verified |
| < 0.6 | ❌ contested |
| 出现 disagree | ❌ contested — 一票否决 |

### L0 定理

```yaml
id: TH-L0-NNN
statement: |
  <从 L0 公理必然推出的结论>

type: l0_theorem

derivation:
  from_axioms: [<AX-L0-NNN>]
  from_concepts: [<CONCEPT-xxx>]
  rule: <conjunction_introduction | modus_ponens | definitional_subsumption>
  formal_steps:
    - "<步骤 1>"
    - "<步骤 N>"
  note: "<为什么不需要经验——仅展开定义中隐含的蕴含>"
```

**目录**：`L0-definitions/theorems/`

**门槛**：推导不引入任何经验假设。每一步是逻辑变换或定义展开。

### 混合定理

```yaml
id: TH-NNN
statement: |
  <L0 结构 × L1 经验 → 关于人类社会的定理>

type: hybrid_theorem

depends_on:
  l0: [<AX-L0-NNN>, <TH-L0-NNN>]
  l1: [<BR-L1-NNN>]

derivation:
  type: empirical_inference
  evidence_weight: <very_strong | strong | moderate | suggestive>
  steps:
    - "L0: <L0 贡献>"
    - "L1: <L1 贡献 (标注 IEA)>"
    - "⇒ <结论>"

corollaries: [<CO-NNN>]
confidence: <very_high | high | moderate | low>
```

**目录**：`deductions/theorems/`

### 推论

```yaml
id: CO-NNN
statement: |
  <可直接用现实检验的具体命题>

derived_from:
  theorem: <TH-NNN>
  l0_axioms: [<AX-L0-NNN>]
  l1_bridging: [<BR-L1-NNN>]
  confidence: <very_high | high | moderate | low>

real_world_anchors:
  - phenomenon: "<具体现实现象>"
    type: <observation | anthropological_record | historical_record | empirical_record>
    source_type: <systematic_review | meta_analysis | empirical_study | case_study | expert_opinion | personal_observation>
    confidence: <very_high | high | moderate | low>
    note: "<局限>"

verification:
  status: <verified | falsified | untested>
  falsifiability: |
    <什么观察会证伪？越具体越好。>

falsification_trace:
  primary_suspect: <BR-L1-NNN>
  failure_mode: "<最可能的失败模式>"
  secondary_suspect: <BR-L1-NNN 或 null>
  failure_mode: "<替代失败模式>"
  unlikely_suspect: <AX-L0-NNN 或 null>
  failure_mode: "<L0 极少出错但如果错了会是怎么错的>"
```

**目录**：`deductions/corollaries/`

**门槛**：至少一个现实锚点 + 可证伪声明 + 追责路径。

---

## Part 3: 研究流程

### 节奏

研究不是流水线。以下是你和 Claude 的对话节奏：

1. **你表达一个洞察** — "我觉得群体的根本属性是..." / "这条公理不太对，因为它..." / "我在想合作是不是可以从..."
2. **Claude 追问和 sharpening** — 动态提问，不是按预写列表。关注你刚才说的具体内容，帮你把它变得更精确、更经得起挑战。
3. **你满意后，Claude 形式化** — 把对话内容写成 YAML 文件，填到你指出的目标目录。
4. **运行 validate.py** — 确保引用和 ID 无断裂。
5. **提交** — 小步提交，每条公理/桥接一个 commit。

### 自然流动

随着研究推进，你自然会穿越不同层次：

- 说"群体有边界" → 这是在 L0 概念层
- "但人类群体的边界是不是有特殊形式？" → 滑入 L1 桥接
- "等等，那'边界'这个概念本身需要先定义清楚" → 回到 L0 概念
- "博弈论里关于边界维护有什么说法？" → 跳到来源层

**所有这些跳跃都是正常的研究行为。** Claude 不会说"我们先做完 L0 再谈 L1"——会跟着你走，同时帮你追踪哪些东西已经形式化了、哪些还在讨论中。

### 收敛信号

当你连续一段时间不再产生新的 L0 公理和 L1 桥接，而是主要在打磨已有的表述、回修措辞、或讨论推论的应用时→接近收敛。此时 Claude 会提醒你考虑 snapshot。

### 快照

当你判断本轮已收敛（参考顶部三个完成标准），制作 `iterations/iter-001/` 下的三个文件：

**snapshot.yaml** — 统计快照：
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
  iea_distribution: {high: <N>, medium: <N>, low: <N>}
  coverage_gaps: [<本轮未覆盖的重要领域>]
  independence_concerns: <N>
```

**diff.yaml**（首轮为 initial）：
```yaml
iteration: 1
diff_from: null
diff_type: initial
summary: "<本轮核心成果的一句话总结>"
```

**CONCLUSION.md** — 自由文本，必须包含：
- 本轮成果概述
- IEA 分析和独立性风险
- 方法论反思（什么运作得好、什么需要改进）
- **已知的未知**（本轮无法解释的现象→iter-002 的种子）
- 下一轮建议

---

## Part 4: 目录速查

```
产出物                          模板    门槛
──────                          ────    ────
L0-definitions/concepts/        L0概念  不含经验假设
L0-definitions/axioms/          L0公理  对抗式 negation_test 通过
L0-definitions/contested/       争议     negation_test 未解决
L0-definitions/theorems/        L0定理  纯演绎，无经验引入

sources/<discipline>/           来源    有文献支撑
sources/cross-verification/     交叉验证  IEA 计票

L1-bridging/candidates/         候选     未投票
L1-bridging/verified/           已验证   IEA ≥ 1.2, 无 disagree
L1-bridging/weakly_verified/    弱验证   0.6 ≤ IEA < 1.2
L1-bridging/rejected/           否决     disagree 一票否决

deductions/theorems/            混合定理  L0 × L1
deductions/corollaries/         推论     锚点 + 可证伪 + 追责路径

iterations/iter-001/            快照     snapshot + diff + CONCLUSION
```

---

## 附录：validate.py 快速参考

```bash
python scripts/validate.py          # 基础检查（ID+引用+状态）
python scripts/validate.py -v       # 详细模式（列出所有实体）
```

每次创建或修改 YAML 文件后运行一次。提交前必须通过。
