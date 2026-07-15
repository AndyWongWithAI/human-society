# L4 作者前置清单 (L4 Author Pre-flight Checklist)

> 用途:**起草 L4 复合推论前**逐条自查。L4 的主前提是 L3 推论（≥2 条），结论必须是涌现的系统性命题。
> 本清单在 L3 清单基础上增加 L4 专属检查项。L3 清单的 A–E 段仍然适用（操作化、射程、锚点、诚实），
> 但 L4 的 A 段替换为"涌现"，D 段加严。

## A. 涌现（替代 L3 的"非平凡性"，L4 的 defining constraint）

- [ ] **必要性**:逐一移除每条 L3 父推论。移除后，L4 的结论还成立吗？若成立 → 该父推论是"观众砖（spectator brick）"，挂名不出力。
- [ ] **新颖性**:L4 至少有一个命题，不是任何单条父推论的断言，也不是父推论 AND/OR 的平凡组合。列出所有父推论的各自结论，逐条对照 L4 的每个核心命题。
- [ ] **多父逐格判空**:画出父推论关键变量的笛卡尔积表。逐格标注"该格预测由哪条父推论强制"。至少一个格子标注为"需要 DED-X + DED-Y 合力"。归零 = 平凡合取（DED-004 的 P2）。
- [ ] **brick=conclusion（L4 版）**:L4 的非平凡内核，是否已经是某条父推论结论的直接复述？"父推论 A 说 X，父推论 B 说 Y，所以 X+Y"不是 L4——那是 AND 拼接。

## B. 操作化（L4 扩展）

- [ ] **复合输出变量的测量独立于各父机制单独输出**：怎么区分"机制 A 和 B 各自独立运作"与"机制 A 和 B 交互产生新东西"？
- [ ] **交互测量**：如果声称"交互效应"，交互项的操作化定义是什么？乘法项？阈值触发？序贯条件？
- [ ] **阈值连口径一次性注册**（L4-009 判例）：起草时所有阈值/判据必须连同分子、分母、测量口径一并写死，不得只写数字留口径空白。为什么：口径若留到边界反例出现后再定，选择方向必被结果污染——届时凡靠事后口径救活的边界案例，审查一律按不利于推论方向计。
- [ ] 标准 L3 操作化检查仍然适用（测量轴正交、anti-talisman、分类判据档位匹配、枚举穷尽）。

## C. 射程与判别

- [ ] **claim_type 正确声明**：`social_form_prediction` / `trajectory_prediction` / `phase_transition` / `co_evolution`——证据标准与声明类型匹配。
- [ ] **判别效度**：如果只读其中一条父推论（不看其他），一个理性的观察者会预测什么？L4 的预测与之有何不同？
- [ ] **防平凡化**：L4 的独特可证伪预测是什么？（不能是"两条父推论都成立"这个平凡合取。）
- [ ] **primary_suspect**：诚实点名最弱的父推论（哪条父推论的脆弱性最威胁 L4 的结论）。

## D. 现实锚（L4 加严）

- [ ] **至少一个锚点是复合/交互特有的**：该锚点的现象不能被任何单条父推论单独解释——必须在案例中观察到父推论机制的**可观察交互**。
- [ ] **至少一个锚点涉及机制交互的可见结果**：不是说"A 存在且 B 存在"，而是"A 和 B 的交互产生了可区别于 A 单独 + B 单独的结果"。
- [ ] **若找不到复合特有锚点**：必须在 `real_world_anchors` 里诚实声明"无复合特有锚点，置信度完全继承自父推论"——使其脆弱性可见。
- [ ] 标准 L3 锚点检查仍然适用（事实核查、独立测出驱动量、反例猎捕先自己做）。

## E. 诚实与依赖

- [ ] **所有 L3 父推论 verified 或 verified\***：不能建在 candidate 推论上（太不稳定）。
- [ ] **依赖闭合**：depends_on.deductions（L3 父前提）≥2 条；depends_on.composite_deductions（L4 父前提）如有，必须无环。
- [ ] **置信度天花板显式声明**：L4 的 status 天花板 = min(所有父推论的 CAP)。在 statement 或 derivation 中注明。
- [ ] **人话摘要**：在场、忠实、非架构人也能懂。L4 离地基更远，更需要人话锚定。
- [ ] **跑 validate.py**：确认实体数 +1、无 ❌ YAML、引用完整、L4 专属检查通过。

---

## 瘦身 canonical L4 格式

```yaml
id: L4-NNN
type: composite_deduction
layer: L4-composites
deduction_form: composite          # L4 固有，不可省略
status: candidate                  # 定论后 → verified / verified* / rejected
term: "中文名 (English Name)"
claim_type: social_form_prediction | trajectory_prediction | phase_transition | co_evolution

人话摘要: "..."                    # 一段，非架构人也能懂

statement: |                       # 规范陈述
  【Composite claim】...
  【Parent mechanisms】...
  【Emergent property】...
  【Prediction】(i)(ii)(iii) ...

operationalization:                # 规则 A：每个量 definition / measurement / limitations
  <自变量>: {definition, measurement, limitations}
  <复合输出变量>: {definition, measurement, limitations}

derivation:
  from_l3:
    deductions: [DED-XXX, DED-YYY]   # 主前提 (≥2)
  from_l1: {axioms: [...], theorems: [...]}
  from_l2: {bridging: [...]}
  from_l4: [L4-NNN, ...]             # 可选
  steps: |
    1. 父机制摘要
    2. 交互逻辑
    3. 涌现论证
    4. 多父逐格判空

emergence_demonstration:           # L4 专属
  necessity: "为什么每条父推论必要..."
  novelty: "什么命题不被任何单父推论包含..."
  multi_parent_cells: "哪些格子需要父推论合力..."

falsifiability: "..."
falsification_trace: {primary_suspect, secondary_suspect, unlikely_suspect}
excluded_outcomes: [...]
real_world_anchors: {supporting: [...], counterexamples: [...], boundary_cases: [...]}
discriminant_validity: "..."
review_summary: "审查后由 finalize 填（≤3 行）"

depends_on:
  axioms: [...]
  theorems: [...]
  bridging: [...]
  concepts: [...]
  deductions: [DED-XXX, DED-YYY]           # L3 父前提
  composite_deductions: [L4-NNN, ...]       # L4 父前提（可选）
domain: [...]
created: YYYY-MM-DD
```
