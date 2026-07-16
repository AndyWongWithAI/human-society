// scripts/l2_verify.workflow.js
// L2 桥接砖验证管线:IEA 调查 → 1 轮对抗审查 → verify/reject
//
// L2 桥接砖(BR-L2-*)是把 L1 抽象概念接到真实人类社会的【经验命题】(如"人类存在
// 不公平厌恶")。它和 L3 推论一样【可错、需对冲】,但此前只有 IEA 多来源加权投票,
// 没有标准化的独立对抗审查流程。本管线补齐这一步。
//
// 调用(单条):
//   Workflow({ scriptPath: '<repo>/scripts/l2_verify.workflow.js',
//              args: { id: 'BR-L2-025', slug: '...', domain: ['...'] } })
// 调用(批量,pipeline 并行、各自独立):
//   Workflow({ scriptPath, args: { ids: ['BR-L2-025','BR-L2-026'], domain: ['...'] } })
// 可选:reviewModel: 'opus'|'haiku'|... —— 审查 agent 用指定模型跑,提供血统级独立性
//   (尤其经验编码/事实核查);省略则退回默认模型(同血统,仍享上下文独立性)。
//
// 与 L3/L4 管线的关键区别:
//   - L2 是"经验砖",不涉及推导链(deduction chaining),没有"父推论"——输入是 L1 实体
//     (axioms/theorems/concepts)+ 跨学科来源(演化生物学/博弈论/文化普适/实验经济学…)。
//   - L2 不需要涌现检查(emergence_demonstration)——它是单机制声称。
//   - L2 验证标准 = IEA 独立性(锚源 1.0,余按成对独立系数折算,≥1.8 verified / ≥1.2 下限)
//     + 机制有效性(brick=conclusion? 测量轴正交? anti-talisman?)。
//   - 只 1 轮审查(L2 比 L3 简单,无多轮迭代、无自动 revise)。
//
// v1 初版,轻量——1 轮审查,无涌现检查,无 revise loop。needs_revision 交主循环裁量。

export const meta = {
  name: 'l2-verify',
  description: 'L2 桥接砖验证 v1:IEA 调查 → 1 轮独立对抗审查 → verify/weakly_verify/reject,轻量单轮',
  phases: [
    { title: 'IEA Survey', detail: '逐来源验证 + 加权 IEA + instrument 折扣披露,写入 cross_verification' },
    { title: 'Review',     detail: 'fresh 实例读 L3 评分卡对抗审查(brick=conclusion/测量轴正交/anti-talisman/反例猎捕)' },
    { title: 'Finalize',   detail: 'verified/weakly_verified 翻牌并归位,rejected 归档,needs_revision 交主循环' },
  ],
}

let b = args || {}
if (typeof b === 'string') {
  try { b = JSON.parse(b) } catch (e) {
    return { error: 'args 是字符串但非合法 JSON', raw: String(b).slice(0, 200) }
  }
}
const REPO = b.repo || '/home/hq/research/human-society'
const INDEPENDENCE = `${REPO}/sources/independence-model.yaml`
const RUBRIC = `${REPO}/docs/pipeline/review-rubric.md`
const INDEX = `${REPO}/INDEX.md`
const REVIEWS_DIR = `${REPO}/L2-bridging/reviews`

// --- 结构化返回 schema(强制紧凑,重产物永不回主循环) ---
const IEA_OUT = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    ieaScore: { type: 'number' },
    sourceBreakdown: { type: 'string' },  // 一行:"锚 behav_econ 1.0 + evo_bio 0.6 + cultural 0.5 = 2.1"
    validatorOk: { type: 'boolean' },
  },
  required: ['done', 'ieaScore', 'validatorOk'],
}
const REVIEW_OUT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['verified', 'needs_revision', 'rejected'] },
    requiredFixes: { type: 'array', items: { type: 'string' } },
    counterexample: { type: 'string' },
    oneline: { type: 'string' },
  },
  required: ['verdict', 'requiredFixes', 'oneline'],
}
const FINALIZE_OUT = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    validatorOk: { type: 'boolean' },
    note: { type: 'string' },
  },
  required: ['done', 'validatorOk'],
}

// ============ 单条 BR 的完整生命周期(IEA → Review → Finalize) ============
async function verifyOne(id, domain) {
  const domainStr = JSON.stringify(domain || [])
  const REVIEW_PATH = `${REVIEWS_DIR}/ADV-REVIEW-${id}.yaml`

  // ---- Phase 1: IEA Survey ----
  phase('IEA Survey')
  const iea = await agent(
    `你是 L2 桥接砖的【IEA 调查员】,全新上下文。目标:对下面这条已写好的桥接砖做
独立来源加权投票(IEA = 独立 agree 当量),把结论写回砖文件的 cross_verification 段。

## 审查对象
桥接砖 ${id}(status 为 candidate;若为 verified/weakly_verified 则本次是【存量回补审查】——同样全流程跑,裁决只能维持或降级,不得因"已 verified"放水)。先用 \`cd ${REPO} && ls L2-bridging/*/${id}-*.yaml\` 定位文件路径,读它。已有 cross_verification 段则以本次重算为准更新。
domain: ${domainStr}

## 封顶读取(两份,不读无关全文)
1. ${INDEPENDENCE} —— 来源两两独立系数 + 【instrument_correlation 仪器折扣】(单 LLM 执行时有效独立性低于学科上限,必须披露)。
2. ${INDEX} 仅在需核对该砖 bridges_to 的 L1 实体(concepts/axioms/theorems)是否存在时打开对应行。

## IEA 调查任务
- 逐来源验证:对该砖 applicable_sources 列出的每一学科通道(演化生物学/博弈论/文化普适/实验经济学…),
  独立判断该来源是否 agree,给 status(agree/disagree/mixed)+ weight + 一句 note(证据+为何独立)。
- 计算加权 IEA:锚源权重 1.0,其余来源按 independence-model 的【成对独立系数】对锚源折算后求和
  (系数缺失用 default_independence)。避免把高度共享数学结构/语料的来源重复计权。
- instrument_disclosure:本次投票由单一 LLM 执行,必须在 verdict_note 显式披露"报告 IEA 是学科独立性上限,
  仪器有效独立性低于此"(照 independence-model 的 discount_rule)。
- 把 votes(逐源)+ iea(数字)+ verdict_note(含折扣披露)写进砖文件的 cross_verification 段。
  【本阶段不改 status——status 由 Finalize 阶段按审查裁决翻牌。】

## 硬要求
- YAML 陷阱:多行叙述段一律用 | 块标量;裸标量里禁 ASCII 冒号+空格(会静默把整块顶飞、实体少一个仍报✅)。
- 跑 \`cd ${REPO} && python scripts/validate.py\`,确认无 ❌ YAML、实体数不减、引用完整。

## 返回(紧凑){done, ieaScore, sourceBreakdown, validatorOk}`,
    { label: `iea:${id}`, phase: 'IEA Survey', schema: IEA_OUT, agentType: 'general-purpose' }
  )

  if (!iea || !iea.validatorOk) {
    return { id, verdict: 'iea_failed', reviewPath: REVIEW_PATH,
             note: iea ? 'IEA 调查产出未过校验' : 'IEA agent 失败', iea }
  }
  log(`${id} IEA done: ${iea.ieaScore} — ${iea.sourceBreakdown || ''}`)

  // ---- Phase 2: Adversarial Review(1 轮) ----
  phase('Review')
  const rev = await agent(
    `你是 L2 桥接砖的【独立对抗审查者】,全新上下文,与写砖者及 IEA 调查员无关。L2 是经验命题、会错,
你的职责是尽最大努力打穿它,给硬裁决。默认怀疑,宁可错杀不放水(最高原则:方法论 > 任何单条命题)。

## 唯一校准来源
L3 评分卡:${RUBRIC}(读它即可——L2 也是经验命题,10 条通用红旗同样适用;**不要**去读其它参照命题)。

## 审查对象
桥接砖 ${id}。用 \`cd ${REPO} && ls L2-bridging/*/${id}-*.yaml\` 定位并读全文(含 IEA 调查刚写入的 cross_verification)。
如需核对 bridges_to 的 L1 实体,查 ${INDEX} 对应行。仪器折扣规则见 ${INDEPENDENCE} 的 instrument_correlation。

## L2 专属重点(在通用 10 红旗之上)
1. **brick=conclusion** — 这条砖是不是只在复述某条 L1 定理/公理?非平凡经验内核在哪?(命中=required)
2. **测量轴正交** — 砖声称的自变量与被观测量是否异源正交?有无隐藏焊点(用结果反推前件)?
3. **anti-talisman** — 前件判定是否不由结果反推?falsifiability 是可事前测的真证伪条件,还是不可证伪护身符?
4. **IEA 独立性诚实** — cross_verification 的独立性假设是否诚实?尤其【单 LLM 执行的折扣是否已披露】?
   有没有把共享数学结构/共享语料的来源当"独立"重复计权而虚高 IEA?
5. **反例猎捕(必做)** — 主动构造/寻找能证伪核心的干净经验案例(跨文化/历史/跨物种)。净杀→rejected/required;
   被消化→记录为何;揭出过度伸张→定位到具体预测列 required。判 verified 前必须留下反例猎捕记录。

## 产出
把本轮完整评审写进 ${REVIEW_PATH} 的 round_1 块(reviewer/verdict/verdict_note/红旗逐条/iea_independence_check/
counterexample_hunt/若非 verified 的 required_fixes)。目录不存在就先创建。用 | 块标量防中文 ASCII 冒号顶飞。
跑 \`cd ${REPO} && python scripts/validate.py\` 确认 YAML 不破。

## 裁决语义
- verified:无 required 级缺陷 + 亲自做过反例猎捕无活反例 + IEA 独立性诚实(单仪器折扣已披露)。
- needs_revision:有可靠定向修订救活的 required/should(列最小清单,交主循环执行——本管线不自动 revise)。
- rejected:核心塌陷(brick=conclusion 无解/测量轴焊死/被净杀反例/IEA 虚高无法诚实达标),改措辞救不活。

## 返回(紧凑){verdict, requiredFixes, counterexample, oneline}`,
    { label: `review:${id}`, phase: 'Review', schema: REVIEW_OUT, agentType: 'general-purpose',
      ...(b.reviewModel ? { model: b.reviewModel } : {}) }
  )

  const verdict = (rev && rev.verdict) || 'needs_revision'
  const fixes = (rev && rev.requiredFixes) || []
  const counterexample = (rev && rev.counterexample) || ''
  log(`${id} review: ${verdict}${fixes.length ? ` — ${fixes.length} fixes` : ''}`)

  // ---- Phase 3: Finalize ----
  // needs_revision:不自动 revise,直接交主循环裁量(L2 比 L3 简单,should 级修改主循环执行更高效)。
  if (verdict === 'verified' || verdict === 'rejected') {
    phase('Finalize')
    // L2 特有:IEA 决定终态 status
    const ieaScore = iea.ieaScore
    let targetStatus = verdict  // 'verified' or 'rejected'
    let moveTo = ''
    if (verdict === 'verified') {
      if (ieaScore >= 1.8) {
        targetStatus = 'verified'
        moveTo = 'L2-bridging/verified/'
      } else if (ieaScore >= 1.2) {
        targetStatus = 'weakly_verified'
        moveTo = 'L2-bridging/weakly_verified/'
      } else {
        return { id, verdict: 'finalize_failed', reviewPath: REVIEW_PATH,
                 note: `IEA ${ieaScore} < 1.2,不该判 verified`, iea: ieaScore }
      }
    } else {
      moveTo = 'L2-bridging/rejected/'
    }
    const oneline = (rev && rev.oneline) || (verdict === 'rejected' ? '核心塌陷,改措辞救不活' : '机制有效,反例猎捕无活反例')
    const chain = `IEA ${ieaScore} + r1 ${verdict}`
    const why = oneline.replace(/'/g, "'\\''")
    const chainEsc = chain.replace(/'/g, "'\\''")
    const targetStatusFlag = targetStatus !== verdict ? `--target-status ${targetStatus}` : ''
    const fin = await agent(
      `Run finalize for ${id} (scripted, zero LLM reasoning):
cd ${REPO} && python scripts/finalize.py ${id} \\
  --verdict ${verdict} ${targetStatusFlag} \\
  --chain '${chainEsc}' \\
  --why '${why}' \\
  --review-num ${id.replace('BR-L2-', '')} \\
  --move-to ${moveTo}
Check stdout for ✅ validate 通过. Return {done, validatorOk, note}.`,
      { label: `finalize:${id}`, phase: 'Finalize', schema: FINALIZE_OUT }
    )
    if (!fin || !fin.validatorOk) {
      return { id, verdict: 'finalize_failed', reviewPath: REVIEW_PATH,
               note: fin ? fin.note : 'finalize 脚本失败', iea: ieaScore }
    }
  }

  return {
    id,
    verdict,
    iea: iea.ieaScore,
    sourceBreakdown: iea.sourceBreakdown,
    core: rev && rev.oneline,
    counterexample,
    requiredFixes: fixes,
    reviewPath: REVIEW_PATH,
    next: verdict === 'verified'
      ? '主循环:校验已过,git add 砖文件+审查档并提交(按授权自主翻牌提交)'
      : verdict === 'rejected'
        ? '主循环:上报 rejected + 归档(诚实记录,毙掉弱砖是加分)'
        : '主循环:needs_revision,按 requiredFixes 定向整改后重跑本管线(本管线不自动 revise)',
  }
}

// ============ 分发:单条 or 批量并行 ============
const ids = Array.isArray(b.ids) ? b.ids : (b.id ? [b.id] : [])
if (!ids.length) {
  return { error: '未提供 id:传 { id: "BR-L2-025", ... } 或 { ids: ["BR-L2-025", ...] }' }
}

if (ids.length === 1) {
  return await verifyOne(ids[0], b.domain)
}

// 批量:各 BR 独立走完整生命周期,pipeline 并行,墙钟 ≈ 单条最慢链
log(`批量验证 ${ids.length} 条 L2 砖:${ids.join(', ')}`)
const results = await parallel(ids.map((id) => () => verifyOne(id, b.domain)))
const summary = results.map((r, i) => r || { id: ids[i], verdict: 'workflow_failed' })
const verified = summary.filter((s) => s.verdict === 'verified').map((s) => s.id)
const other = summary.filter((s) => s.verdict !== 'verified')

return {
  batch: ids.length,
  verified,
  needsAttention: other.map((s) => ({ id: s.id, verdict: s.verdict })),
  all: summary,
  next: verified.length
    ? `主循环:${verified.join('/')} 已 verified 且过校验,git add 各自砖文件+审查档并提交;其余(${other.map((s) => s.id + ':' + s.verdict).join(', ') || '无'})上报`
    : '主循环:无 verified,逐条上报',
}
