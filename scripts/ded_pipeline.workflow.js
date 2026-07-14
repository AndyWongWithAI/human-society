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
//   repo: '/home/hq/research/human-society'  // 可选
// }

export const meta = {
  name: 'ded-pipeline',
  description: '公理化推论管线:author(带前置清单)→ adaptive 对抗审查 loop → 定论,轮间不过主循环,只回紧凑裁决',
  phases: [
    { title: 'Author',   detail: '按前置清单起草瘦身 candidate DED' },
    { title: 'Review',   detail: 'fresh 实例读评分卡对抗审查,自写档,只回紧凑裁决' },
    { title: 'Revise',   detail: '按 required 定向 Edit,不整份重写' },
    { title: 'Finalize', detail: 'verified 翻牌 / rejected 归档,回紧凑摘要' },
  ],
}

let b = args || {}
// harness 有时把对象 args 序列化成 JSON 字符串;兼容两种传法。
if (typeof b === 'string') {
  try { b = JSON.parse(b) } catch (e) {
    return { error: 'args 是字符串但非合法 JSON', raw: String(b).slice(0, 200) }
  }
}
const REPO = b.repo || '/home/hq/research/human-society'
const MAX = b.maxRounds || 3

// --- 基本校验:缺关键 brief 字段直接回错,不空跑 ---
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

// --- 结构化返回 schema(强制紧凑) ---
const AUTHOR_OUT = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    coreOneLine: { type: 'string', description: '推论核心一句话' },
    validatorOk: { type: 'boolean', description: 'validate.py 是否通过且实体+1、无 ❌ YAML' },
  },
  required: ['done', 'coreOneLine', 'validatorOk'],
}
const REVIEW_OUT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['verified', 'needs_revision', 'rejected'] },
    requiredFixes: { type: 'array', items: { type: 'string' }, description: 'required/should 最小清单,每条一行;无则空数组' },
    counterexample: { type: 'string', description: '反例猎捕结果一句话' },
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

## 先做(封顶读取成本,别整份扫 L3-deductions/)
先跑 \`cd ${REPO} && python scripts/index.py\` 重生实体索引,再读 ${INDEX}——它一行一条列出所有已有实体(id/status/term/摘要/依赖)。用它了解已有推论、**避免与既有推论重叠**、找对齐判别的对象;只在真需核对某条全文时才打开那一两份。

## 必读
1. 前置清单 + 瘦身格式规范:${CHECKLIST}(务必读完,起草前逐条自查 A–E,格式照"瘦身 canonical DED 格式"节)
2. 承重砖(逐份读,推论只能引已 verified 的砖):${bricks}(在 ${REPO}/L2-bridging/verified/<id>-*.yaml)

## 要写的推论
- id: ${b.id}   term 用中文名(English)
- 主题: ${b.title}
- 论点/承重逻辑/招牌预测:
${b.thesis}
- 核心一句话(人话摘要与 statement 对齐): ${b.coreClaim || '(从论点提炼)'}
- domain: ${domain}
- 承重砖: ${bricks}

## 硬要求
- 严格按前置清单【瘦身格式】写,只放规范 claim;审查史留给 ADV-REVIEW,别在 DED 里开 adversarial_review 全过程(只需 review_summary 占位一行)。
- 起草时把清单 A(逐格判空)、B(操作化/测量轴正交/anti-talisman)、C(射程独立/primary_suspect/判别)真正落到对应字段;nontriviality_test 与 falsification_trace 必写。
- **YAML 陷阱**:多行段一律 \`|\` 字面块标量;别在裸标量写 ASCII 冒号+空格(会把块顶飞)。
- 写到 ${DED_PATH};写完跑 \`cd ${REPO} && python scripts/validate.py\`,确认实体数 +1 且【无 ❌ YAML】、引用完整。

## 返回(紧凑,勿复述全文)
{done, coreOneLine, validatorOk}`,
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
评分卡:${RUBRIC}(读它即可,**不要**去读其它参照推论 DED-006/007 等——那是浪费)。

## 已有实体上下文(按需)
如需了解本推论与已有实体的关系(判别/重叠),读定长索引 ${INDEX},别整份扫其它推论全文。

## 审查对象
${DED_PATH}(status: candidate)。承重砖如需核对 brick=conclusion:${bricks}(在 ${REPO}/L2-bridging/verified/)。
${round > 1 ? `前几轮记录在 ${REVIEW_PATH},读 round_1..round_${round - 1} 了解已修什么,别重复已解决的点。` : ''}

## 任务
按评分卡红旗逐条攻 + 反例猎捕(必做,判 verified 前尤其)。裁决语义、verified 三条门、返回格式全照评分卡。
把本轮完整评审写进 ${REVIEW_PATH} 的 \`round_${round}\` 块(该文件${round === 1 ? '需新建,含 id: ADV-REVIEW-' + b.reviewNum + '、type: adversarial_review、reviews: ' + b.id + '、target、protocol,及 round_1' : '已存在,只加/改 round_' + round + ',勿动别轮'})。写完跑 \`cd ${REPO} && python scripts/validate.py\` 确认 YAML 不破(长段用 \`|\`)。

## 返回(紧凑){verdict, requiredFixes, counterexample, oneline}`,
    { label: `review:${b.id}:r${round}`, phase: 'Review', schema: REVIEW_OUT, agentType: 'general-purpose' }
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
- 只 Edit 受影响的段落,保持瘦身格式;每处改动要真正消解对应 required(不是敷衍加句话)。
- 在 ${DED_PATH} 的 review_summary 追加/更新一行本轮结论;若需记作者回应,写进 ${REVIEW_PATH} 的 author_response_round_${round}(别塞回 DED)。
- YAML 陷阱同前(\`|\` 块标量)。改完跑 \`cd ${REPO} && python scripts/validate.py\` 确认无 ❌ YAML、引用完整。

## 返回(紧凑){done, validatorOk, note}`,
    { label: `revise:${b.id}:r${round}`, phase: 'Revise', schema: REVISE_OUT, agentType: 'general-purpose' }
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
    `把 ${DED_PATH} 的 status 由 candidate 改为 verified;更新 review_summary(r1..r${round} 轨迹 + 一句话为何 verified + 指向 ${REVIEW_PATH});补 revised 日期与 revision_note 摘要。跑 \`cd ${REPO} && python scripts/validate.py\` 确认无 ❌ YAML、状态检查通过。返回 {done, validatorOk, note}。`,
    { label: `finalize:${b.id}`, phase: 'Finalize', schema: REVISE_OUT, agentType: 'general-purpose' }
  )
}

return {
  id: b.id,
  verdict,          // verified / needs_revision / rejected
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
