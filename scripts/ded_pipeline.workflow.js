// scripts/ded_pipeline.workflow.js
// 公理化推论管线:author(带前置清单,写瘦身 candidate)→ adaptive 对抗审查 loop
// (fresh 实例、读评分卡、自写档、只回紧凑裁决)→ revise(定向 Edit)→ finalize(verified 翻牌)。
// 重产物(全文 YAML / 全文审查)永不回主循环;只回 {id, verdict, rounds, paths, core}。
//
// 调用:Workflow({ scriptPath: '<repo>/scripts/ded_pipeline.workflow.js', args: BRIEF })
// BRIEF = {
//   id: 'DED-009', slug: 'kin-vs-merit-recruitment', reviewNum: '014',
//   title: '亲缘 vs 绩效的组织录用均衡',
//   thesis: '多行:要证什么、承重逻辑、招牌预测',
//   coreClaim: '一句话核心(供人话摘要与 statement 对齐)',
//   bricks: ['BR-L2-002','BR-L2-010'],       // 承重砖 id(在 L2-bridging/verified/)
//   domain: ['政治社会学','组织理论','亲属制度'],
//   maxRounds: 3,                            // 可选,默认 3
//   reviewModel: 'opus',                     // 可选,审查/整改 agent 用指定模型(如 'opus'/'haiku'),
//                                            // 提供血统级独立性;不设=继承主模型(author/finalize 永远继承主模型)
//   repo: '/home/hq/research/human-society'  // 可选
// }
//
// v2 效率优化 (2026-07-15):
// - Author 不跑 index.py 再生(浪费),不逐份读 L2 砖全文(INDEX 摘要够用)
// - Reviewer r2+ 不读全量旧审查档(改读 DED review_summary 紧凑摘要)
// - Revise 阶段自动将本轮裁决压进 DED review_summary

export const meta = {
  name: 'ded-pipeline',
  description: '公理化推论管线 v2:author(INDEX+清单)→ adaptive 对抗审查 loop → 定论,轮间不过主循环',
  phases: [
    { title: 'Author',   detail: '读 INDEX+清单起草瘦身 candidate,砖仅读摘要行' },
    { title: 'Review',   detail: 'fresh 实例读评分卡对抗审查,读 DED review_summary 而非全量旧审查' },
    { title: 'Revise',   detail: '定向 Edit,写 DED review_summary 紧凑摘要供下轮复用' },
    { title: 'Finalize', detail: 'verified 翻牌 / rejected 归档' },
  ],
}

let b = args || {}
if (typeof b === 'string') {
  try { b = JSON.parse(b) } catch (e) {
    return { error: 'args 是字符串但非合法 JSON', raw: String(b).slice(0, 200) }
  }
}
const REPO = b.repo || '/home/hq/research/human-society'
const MAX = b.maxRounds || 3

const missing = ['id', 'slug', 'reviewNum', 'title', 'thesis'].filter((k) => !b[k])
if (missing.length) {
  return { error: `brief 缺字段: ${missing.join(', ')}`, hint: '见脚本顶部 BRIEF 示例' }
}

const DED_PATH = `${REPO}/L3-deductions/corollaries/${b.id}-${b.slug}.yaml`
const REVIEW_PATH = `${REPO}/L3-deductions/reviews/ADV-REVIEW-${b.reviewNum}-${b.id}.yaml`
const CHECKLIST = `${REPO}/docs/pipeline/author-checklist.md`
const RUBRIC = `${REPO}/docs/pipeline/review-rubric.md`
const INDEX = `${REPO}/INDEX.md`
const bricks = (b.bricks || []).join(', ')
const domain = JSON.stringify(b.domain || [])

const AUTHOR_OUT = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    coreOneLine: { type: 'string' },
    validatorOk: { type: 'boolean' },
  },
  required: ['done', 'coreOneLine', 'validatorOk'],
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
const REVISE_OUT = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    validatorOk: { type: 'boolean' },
    note: { type: 'string' },
  },
  required: ['done', 'validatorOk'],
}

// ============ Phase 1: Author ============
phase('Author')
const authored = await agent(
  `你是公理化推论【作者】,全新上下文。目标:把下列推论写成一份【瘦身 canonical】的 candidate YAML。

## 封顶读取(两份)
1. 读 ${INDEX}(定长索引,一行一条实体)——了解已有推论、避免重叠、找判别对象。
2. 读 ${CHECKLIST}(前置清单+瘦身格式)——逐条自查 A–E,照底部"瘦身 canonical DED 格式"节写。
3. 承重砖 ${bricks} ——【仅读 INDEX 摘要行,不逐份读全文】。
   起草中遇到具体歧义时再打开对应砖全文 (${REPO}/L2-bridging/verified/<id>-*.yaml)。

## 要写的推论
- id: ${b.id}   主题: ${b.title}   核心一句话: ${b.coreClaim || '(从论点提炼)'}
- domain: ${domain}   承重砖: ${bricks}
- 论点/承重逻辑/招牌预测:
${b.thesis}

## 硬要求
- 瘦身格式照清单底部节。必填:nontriviality_test / falsification_trace / primary_suspect。
- YAML 陷阱:多行段用 | 块标量,裸标量禁 ASCII 冒号+空格。
- 写到 ${DED_PATH};跑 \`cd ${REPO} && python scripts/validate.py\`,确认实体+1、无 ❌、引用完整。

## 返回(紧凑){done, coreOneLine, validatorOk}`,
  { label: `author:${b.id}`, phase: 'Author', schema: AUTHOR_OUT, agentType: 'general-purpose' }
)

if (!authored || !authored.validatorOk) {
  return { id: b.id, verdict: 'author_failed', rounds: 0, dedPath: DED_PATH,
           note: authored ? '作者产出未过校验' : '作者 agent 失败', authored }
}
log(`author done: ${authored.coreOneLine}`)

// ============ Phase 2: adaptive Review / Revise loop ============
let round = 0
let verdict = 'needs_revision'
let fixes = []
let lastCounterexample = ''

while (round < MAX) {
  round++
  phase('Review')
  const rev = await agent(
    `你是【独立对抗审查者】(round ${round}),全新上下文,与作者及前几轮审查者无关。

## 唯一校准来源
评分卡:${RUBRIC}(读它即可,**不要**去读其它参照推论——那是浪费)。

## 审查对象
${DED_PATH}(status: candidate)。
承重砖如需核对:${bricks}（在 ${REPO}/L2-bridging/verified/,仅在真需核对事实时打开全文）。
${round > 1 ? `**前轮摘要** (已在 DED 文件的 review_summary 字段,读它即可——不读全量旧审查档,那是浪费):\n读 ${DED_PATH} 的 review_summary 字段,含 r1–r${round - 1} 紧凑结论。仅在 review_summary 有歧义或需核对前轮细节时,再打开 ${REVIEW_PATH} 对应 round。` : ''}

## 任务
按评分卡红旗逐条攻 + 反例猎捕(必做)。裁决语义、verified 三条门、返回格式全照评分卡。
把本轮完整评审写进 ${REVIEW_PATH} 的 round_${round} 块。
跑 \`cd ${REPO} && python scripts/validate.py\` 确认 YAML 不破。

## 返回(紧凑){verdict, requiredFixes, counterexample, oneline}`,
    { label: `review:${b.id}:r${round}`, phase: 'Review', schema: REVIEW_OUT, agentType: 'general-purpose', ...(b.reviewModel ? { model: b.reviewModel } : {}) }
  )

  verdict = (rev && rev.verdict) || 'needs_revision'
  fixes = (rev && rev.requiredFixes) || []
  lastCounterexample = (rev && rev.counterexample) || ''
  log(`round ${round}: ${verdict}${fixes.length ? ` — ${fixes.length} fixes` : ''}`)

  if (verdict === 'verified' || verdict === 'rejected') break
  if (!fixes.length) { log(`round ${round}: needs_revision 但无 required,停(交主循环裁量)`); break }

  phase('Revise')
  const revised = await agent(
    `你是【整改者】,全新上下文。按 round-${round} 审查的 required 清单,对推论做【定向 Edit】(勿整份重写)。

## 输入
- 推论文件:${DED_PATH}
- 本轮 required 清单:
${fixes.map((f, i) => `  ${i + 1}) ${f}`).join('\n')}
- 审查全档:${REVIEW_PATH} 的 round_${round}(如需上下文)

## 硬要求
- 只 Edit 受影响的段落,保持瘦身格式;每处改动真正消解对应 required。
- **【关键】在 ${DED_PATH} 的 review_summary 追加本轮 compact 摘要**(1–2 行):本轮裁决词 + 修复的核心红旗 + "见 round_${round}"。这行是下轮审查者的"前轮摘要"。
- 若需记详细作者回应,写进 ${REVIEW_PATH} 的 author_response_round_${round}(不塞回 DED)。
- YAML 陷阱同前(| 块标量)。跑 \`cd ${REPO} && python scripts/validate.py\` 确认无 ❌、引用完整。

## 返回(紧凑){done, validatorOk, note}`,
    { label: `revise:${b.id}:r${round}`, phase: 'Revise', schema: REVISE_OUT, agentType: 'general-purpose', ...(b.reviewModel ? { model: b.reviewModel } : {}) }
  )
  if (!revised || !revised.validatorOk) {
    log(`round ${round}: 整改未过校验,停`)
    return { id: b.id, verdict: 'revise_failed', rounds: round, dedPath: DED_PATH, reviewPath: REVIEW_PATH }
  }
}

// ============ Phase 3: Finalize ============
if (verdict === 'verified') {
  phase('Finalize')
  await agent(
    `把 ${DED_PATH} 的 status 由 candidate 改为 verified。

更新 review_summary —— 【严格 <=3 行,只留结论+指针,禁止复述每轮 required/整改细节(那是双存,归 ADV-REVIEW)】,照此模板(用 | 块标量):
  1) r1 <verdict> -> r2 <verdict> -> ... -> 定论 verified(只写裁决词)
  2) 一句话为何 verified(核心载重新意 + 反例猎捕无活反例)
  3) 全档见 ADV-REVIEW-${b.reviewNum}。

补 revised 日期与 revision_note(一行摘要)。跑 \`cd ${REPO} && python scripts/validate.py\` 确认无 ❌ YAML、状态检查通过。返回 {done, validatorOk, note}。`,
    { label: `finalize:${b.id}`, phase: 'Finalize', schema: REVISE_OUT, agentType: 'general-purpose' }
  )
}

return {
  id: b.id,
  verdict,
  rounds: round,
  core: authored.coreOneLine,
  counterexample: lastCounterexample,
  dedPath: DED_PATH,
  reviewPath: REVIEW_PATH,
  next: verdict === 'verified'
    ? '主循环:校验已过,git add 两文件并提交(按授权自主提交)'
    : verdict === 'rejected'
      ? '主循环:上报 rejected + 归档(诚实记录)'
      : '主循环:needs_revision 未收敛,人工裁量',
}
