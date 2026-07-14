# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

人类社会公理化体系:从几条近乎不可否认的出发点,一步步推出关于人类社会的、**可证伪**的结论。方法论质量 > 任何单条结论(见"最高原则")。

面向人的仪表盘:先读 [`导读.md`](导读.md) + [`术语表.md`](术语表.md)——零黑话,读懂即可治理全局。本文件是给引擎室(未来 Claude)的。

## 常用命令

```bash
python scripts/validate.py    # 一致性校验 = 本仓库的"测试"。改任何实体后必跑。
python scripts/index.py       # 重生 INDEX.md(实体紧凑索引)。增删改实体后跑。
```

- `validate.py` 是唯一的门。它遍历所有含 `id` 的 YAML(跳过 `docs/ iterations/ __pycache__/` 与 `independence-model.yaml`/`META.yaml`),检查:ID 唯一、引用完整、无循环依赖、状态合法、**Rule D confidence_floor**(子推论 status 不得高于父推论允许的上限)、L3 推论必须有 `falsification_trace.primary_suspect` + `real_world_anchors`、L2 verified 必须 `IEA ≥ 1.2`。退出码非 0 即有错。
- **没有单元测试框架**;正确性靠 `validate.py` + 独立对抗审查(见下)。

## 五层架构(核心不变量)

```
L0 物理约束 → L1 定义层 → L2 桥接层 → L3 推论层 → L4 复合推论层
L0-physical/  L1-definitions/  L2-bridging/  L3-deductions/  L4-composites/
```

- **L0**(物理铁律,如熵增/能量守恒/时空):不验证,被上层大量引用当地基。
- **L1**(concepts/axioms/theorems/contested):分析性真理,靠定义 + "否定它就没法说话"成立,不靠观察。
- **L2**(bridges,BR-L2-*):把 L1 接到现实的经验命题,**会错、可被推翻**。
- **L3**(deductions,DED-*):L1 × L2 → 可检验的单机制命题。
- **L4**(composites,L4-*):L3 推论组合 → 关于社会形态与演化轨迹的系统性命题。必须证明涌现(整体 > 部分之和)。

**依赖铁律(validate.py 强制)**:上层只引下层,下层不引上层,谁也不许绕圈。`composed_of` 逐层(L_n 只引 L_{n-1});物理依赖 L3 可直引 L0。

## L3 推论生命周期(要读多个文件才懂的关键流程)

每条推论走:`candidate → 独立对抗审查(N 轮) → 整改 → 定论`。这是本仓库最核心、最花力气的机制。

- **作者 ≠ 审查者**:审查【必须】派一个**全新独立上下文的子 Agent**做(main loop 不得自审)。这是防自欺的结构保证。
- 每条推论配一份 `L3-deductions/reviews/ADV-REVIEW-NNN-*.yaml`,是审查全过程的**单一存档**(推论文件里只留 `review_summary` 3 行 + 指针,不双存)。
- **验证规则 A–D**:A 操作化 → B 独立对抗审查 → C 经验对照 → D 链式(confidence_floor)。附 `anti_talisman_clause`(防不可证伪护身符)+ `nontriviality_test`(逐格判空)。
- **status 枚举**:L3 = `candidate|verified|verified*|rejected`;L2 = `candidate|verified|weakly_verified|rejected`。`verified*` = 带未了悬案(如 DED-003)。`rejected` 是正常产出,不删——体系肯毙自己的推论正是可信度来源(当前已否决 DED-004、DED-007)。
- **沉淀的通用检验**(历次审查换来的红旗)全部写在 `docs/pipeline/author-checklist.md`(作者起草前自查)与 `docs/pipeline/review-rubric.md`(审查者据此攻)。**新增推论前先读这两份**。典型红旗:brick=conclusion、逐格判空、测量轴正交、射程钩子独立于结果、分类判据档位匹配、枚举穷尽须按判据本身定义、anti-talisman 须独立于结果测量、锚点事实核查。

## L2 桥接层验证:IEA(独立 agree 当量)

L2 砖靠多来源加权投票(演化生物学 / 博弈论 / 文化普适),来源间独立系数在 `L2-bridging/independence-model.yaml`。锚源 1.0,其余按成对独立系数打折求和。`IEA ≥ 1.8` = 两个准独立来源(verified);`≥ 1.2` 为下限。`instrument_disclosure` 诚实标注"多路投票实由单一 LLM 执行,有效独立性低于学科上限"。

## 提速管线与 token 纪律

- **碰存量实体先读 `INDEX.md`**(定长紧凑索引,一行一条),别整份扫 L3 全文——读取成本随实体数封顶而非滚雪球。
- 新增推论走 `scripts/ded_pipeline.workflow.js`(Workflow 工具:`Workflow({scriptPath, args: BRIEF})`,brief 格式见脚本顶部)。它编排 author(带前置清单、起始重生索引)→ 自适应审查 loop(fresh 实例、读评分卡、自写档、只回紧凑裁决)→ revise → finalize,轮间不过 main loop、重产物不回主上下文。

## 操作约束(不可从代码发现,务必遵守)

- **最高原则:方法论质量 > 任何单条推论。** 宁可毙掉自己写的弱推论,不放水。用户有最终否决权,包括否决 AI 判断。
- **可分发的工作(尤其独立对抗审查)必须派子 Agent**,main loop 只做编排/守门,不自己当审查者或抄写员。
- **人话摘要强制**:每个实体必带一句非黑话摘要;`导读.md`/`术语表.md` 必须保持零黑话——读不懂它们=体系飘了。
- **提交策略**:单研究者仓库,直接提交 `main`。仅在用户明说"提交"时提交;例外——独立审查判 `verified` 的推论可按既定授权自主翻牌 + 提交,`rejected` 则上报用户。凭据在仓库外(`~/.claude/secrets.json`),永不入库。
- **YAML 陷阱(踩过两次)**:多行叙述段一律用 `|` 字面块标量;裸标量里的 ASCII 冒号+空格(如 `三 species:`)会被当 mapping、**静默**把整块顶飞、实体少一个却仍报"✅通过"——改完务必核对 `validate.py` 的实体数 +1 且无 `❌ YAML`。

## 目录速览

`sources/` 跨来源证据材料 · `iterations/iter-*/CONCLUSION.md` 阶段性结论 · `docs/design/` 设计文档 · `docs/plans/` 实施计划 · `docs/pipeline/` 作者清单+审查评分卡 · `L4-composites/` 复合推论层。当前各推论状态与计数以 `INDEX.md` 为准(`导读.md` 的"三条已验证"是早期快照,已过时)。
