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
// 阅读包(v2.1):审查者冷启动只读 1 份而非 2 份,未命中输入成本 ↓25-40%
const REVIEWER_PACK = `${REPO}/docs/pipeline/reviewer-pack.md`
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
    validatorOk: { type: 'boolean' },
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

  // ---- Phase 1: IEA Survey (免费模型 + Python 算术, v3.0) ----
  // 此前 IEA 段走 pro agent(来源判定+算术+YAML 全付费)。
  // v3.0: iea_survey.py 用免费模型(glm-4-flash/智谱独立血统)做来源定性判断,
  // Python 做系数查表+算术(精确),Agent tool 只当命令执行器(token 量极小)。
  phase('IEA Survey')
  const ieaProvider = b.ieaProvider || 'zhipu'  // 默认智谱(独立血统),可切 sensenova
  const iea = await agent(
    `Run IEA survey for ${id} via free model + Python arithmetic (zero pro LLM cost):

cd ${REPO} && python scripts/iea_survey.py ${id} --provider ${ieaProvider}

Read the JSON result from stdout (format: {"done": true/false, "ieaScore": N, "sourceBreakdown": "...", "validatorOk": true/false}). Return it.`,
    { label: `iea:${id}`, phase: 'IEA Survey', schema: IEA_OUT }
  )

  if (!iea || !iea.validatorOk) {
    return { id, verdict: 'iea_failed', reviewPath: REVIEW_PATH,
             note: iea ? 'IEA 调查产出未过校验' : 'IEA agent 失败', iea }
  }
  log(`${id} IEA done: ${iea.ieaScore} — ${iea.sourceBreakdown || ''}`)

  // ---- Phase 2: Adversarial Review(1 轮) ----
  phase('Review')
  // v4.0: Review 段改用 MiniMax-M3 异血统承重墙（ICV 协议）。
  // Author=glm-5.2(智谱系) × Review=MiniMax-M3(minimax系) = 真正血统独立。
  // L2 专属重点（brick=conclusion/测量轴正交/anti-talisman/IEA独立性诚实/反例猎捕）已在通用评分卡16红旗覆盖。
  const reviewRel = REVIEW_PATH.replace(REPO + '/', '')
  const rev = await agent(
    `Run MiniMax-M3 adversarial review for ${id} round 1 (异血统承重墙, ICV 协议, L2 经验砖):

cd ${REPO} && python scripts/review_minimax.py ${id} \\
  --review-round 1 \\
  --review-path '${reviewRel}' \\
  --layer L2

Read JSON from stdout ({"done","validatorOk","verdict","requiredFixes":[...],"counterexample","oneline"}).
If done=false, report the note. Return only: {verdict, requiredFixes, counterexample, oneline, validatorOk}.`,
    { label: `review:${id}`, phase: 'Review', schema: REVIEW_OUT }
  )
  if (!rev || rev.validatorOk === false) {
    return { id, verdict: 'review_failed', reviewPath: REVIEW_PATH,
             note: rev ? (rev.oneline || '审查档未过校验') : 'review agent 失败' }
  }

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
