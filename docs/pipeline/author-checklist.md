# 作者前置清单 (Author Pre-flight Checklist)

> 用途:**起草推论前**逐条自查,把已知红旗在【上游】消掉,让推论"洗干净了才进审查"。
> 这是把质量从下游返工搬到上游预防——每条都是历次审查用真代价换来的教训。
> 审查评分卡见 `review-rubric.md`(同一批红旗,审查者据此攻)。

## A. 非平凡性(最先自查)

- [ ] **逐格判空**:把推论的核心画成 2×N 判据表(自变量档 × 被预测量档)。**每一格问:是被承重砖【平凡地】强制的吗?** 至少要有一个格是【预测为空/非空可满足】的真经验主张(不是同义反复)。空格必须可被现实反例填上才算数。
- [ ] **brick=conclusion**:推论的非平凡内核,是否【原文或近义】已写在某块承重砖里?若是 → 这不是推论,是砖的复述。特别警惕"专为这条推论窄化的砖"。
- [ ] **砖的边际贡献诚实**:每块承重砖各自单独给出什么?哪块偏"近定义"(只界定概念)、哪块是真发动机?点明,别让近定义砖冒充非平凡来源。

## B. 操作化(防不可证伪)

- [ ] **条件是下定义还是做预测**:核心命题里每个关键条件——是在偷偷下定义(必然为真),还是可证伪的预测?定义不算能力。
- [ ] **测量轴正交**(DED-007 死因):自变量与被预测量,是否在【彼此独立】的轴上测?有没有隐藏焊点——某个自变量偷偷用结果来测?典型:分母别用"实际获授者"(混入结果),要用"合格候选池"。
- [ ] **anti-talisman 真兑现**:判定"是否发生 X"(突破/俘获/侵蚀)时,必须【独立于结果】结构测,不得由"结果发生了"反推"前件成立"。而且——至少一个承重锚要像 DED-005 卡拉哈里、DED-006 集市、DED-008 科举回避那样,**真的独立测出了驱动量**,不是嘴上说说。
- [ ] **分类判据档位匹配**(DED-006):若做分档/分类,档位数要匹配被救对象的档位(连续量别用二分判据)。
- [ ] **枚举穷尽 + species 按判据定义**(DED-007/008):若声称"N 类可枚举/可解离"——(1) 每类必须按【伞级判据本身】定义,不能按某个相关但【不等价】的表征(DED-008:按"是否分享偏私收益"而非"亲缘网内外");(2) 主动猎"第 N+1 类";(3) 先证各测量维度正交。

## C. 射程与判别

- [ ] **射程/排除钩子独立于结果**(DED-005):excluded_outcomes 按【可事前测的渠道】划,不是事后按结果开脱。排除的东西要能事前认出。
- [ ] **primary_suspect 指对**:诚实点名最弱的承重环节(招牌预测压在哪条腿上),并写进 `falsification_trace`。
- [ ] **判别效度 + 防平凡化**:相对相邻已知理论(韦伯/North/委托-代理…),本推论【独有的可证伪预测】是什么?写一条"防平凡化守卫":把非平凡内核精确定位(通常在驱动量归因 / 可逆单调 / 特定失败渠道),别把权重压在会被吸收进常识的卖点上。

## D. 现实锚(防事实错)

- [ ] **事实核查**:每个历史/经验锚,核对基本事实(DED-007 死在战俘营锚的事实反转)。宁可少锚,不可错锚。
- [ ] **至少一个锚独立测出驱动量**(呼应 anti-talisman):`independent_*_evidence` 字段兑现"不看结果也能测出前件"。
- [ ] **反例猎捕先自己做一遍**:主动找一个能证伪核心的干净反例,消化或诚实认伤。别把这活全留给审查者。

## E. 诚实与依赖

- [ ] **人话摘要**:在场、忠实、非架构人也能懂。
- [ ] **新砖的 IEA/status 诚实**:若顺带建 L2 砖,IEA 权重与独立系数照实,不为凑 verified 灌水。
- [ ] **依赖闭合**:depends_on 里的 axioms/theorems/bridging/concepts 全部真实存在(跑 validate.py)。

---

## 瘦身 canonical DED 格式(单一存档,审查史不双存)

DED 文件**只放规范 claim**,审查全过程**只存 ADV-REVIEW-NNN 一处**,DED 里留 3 行摘要 + 指针。目标 ~120–160 行,不是 350+。

```yaml
id: DED-NNN
type: deduction
layer: L3-deductions
status: candidate            # 定论后 → verified / verified* / rejected
term: "中文名 (English Name)"

人话摘要: "..."              # 一段,非架构人也能懂

statement: |                 # 规范陈述:核心 / 驱动量 / 预测 / 与现有理论判别
  【核心】... 【驱动量】... 【预测】(i)(ii)(iii) ... 【判别】...

operationalization:          # 规则 A:每个量 definition / measurement / limitations
  <自变量>: {definition, measurement, limitations}
  <被预测量>: {definition, measurement, limitations}

derivation:
  from_l1: {axioms: [...], theorems: [...]}
  from_l2: {bridging: [...]}
  steps: |                    # ← 必须用 | 字面块标量(见下 YAML 陷阱)
    1. "..." ...
    2. "..." ...
    ...非平凡性(逐格判空)写在最后一步...

falsifiability: |            # (a)(b)(c) 可证伪条件;必要时标注适用区间
falsification_trace: {primary_suspect, secondary_suspect, unlikely_suspect, note}
excluded_outcomes: [...]     # 射程外,按渠道划
anti_talisman_clause: |      # 防不可证伪护身符,独立于结果测量
nontriviality_test: |        # 逐格判空的结论:哪一格预测为空、为何非空可满足
real_world_anchors: {supporting: [...], counterexamples: [...], boundary_cases: [...]}
discriminant_validity: |     # 独有可证伪预测 + 防平凡化守卫

review_summary: |            # ← 只留 3 行,不放全过程
  r1 <verdict> → r2 <verdict> → r3 <verdict>。全档见 ADV-REVIEW-NNN。
  一句话:<最终为何 verified/rejected>。

depends_on: {axioms, theorems, bridging, concepts}
domain: [...]
created: YYYY-MM-DD
```

### YAML 陷阱(踩过两次,务必守)

- **多行叙述段一律用 `|` 字面块标量**(statement / derivation.steps / falsifiability / anti_talisman_clause / …)。
- **别在裸标量里写 ASCII 冒号+空格或行尾冒号**——`达成有三 species:` 这种会被 YAML 当成 mapping,静默把整块顶飞、实体少一个还报"✅通过"。中文冒号"："或用 `|` 块规避。
- 改完**必跑** `cd <repo> && python scripts/validate.py`,确认实体数 +1 且无 `❌ YAML`。
