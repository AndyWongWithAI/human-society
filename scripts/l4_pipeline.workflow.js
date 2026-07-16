// scripts/l4_pipeline.workflow.js
// L4 复合推论管线:author(读 INDEX+清单,写瘦身 candidate)→ adaptive 对抗审查 loop
// (fresh 实例、读评分卡、自写档、只回紧凑裁决)→ revise(定向 Edit)→ finalize(verified 翻牌)。
// 重产物(全文 YAML / 全文审查)永不回主循环;只回 {id, verdict, rounds, paths, core}。
//
// 调用:Workflow({ scriptPath: '<repo>/scripts/l4_pipeline.workflow.js', args: BRIEF })
// BRIEF = {
//   id: 'L4-001', slug: 'state-formation-trajectories', reviewNum: 'L4-001',
//   title: '国家形成轨迹',
//   thesis: '多行:要证什么、承重逻辑、招牌预测',
//   coreClaim: '一句话核心(供人话摘要与 statement 对齐)',
//   l3Parents: ['DED-012','DED-010','DED-006'],   // L3 主前提(>=2 条 verified L3 推论)
//   l4Parents: ['L4-001','L4-002'],               // L4 父前提(可选)
//   claimType: 'social_form_prediction',
//   domain: ['国家形成','政治经济学','制度演化'],
//   maxRounds: 3,                                   // 可选,默认 3
//   reviewModel: 'opus',                            // 可选,审查/整改 agent 用指定模型(如 'opus'/'haiku'),
//                                                   // 提供血统级独立性;不设=继承主模型(author/finalize 永远继承主模型)
//   repo: '/home/hq/research/human-society'         // 可选
// }
//
// v2 效率优化 (2026-07-15):
// - Author 不读 METHODOLOGY(清单已含规则 E/F/G),不逐份读 L3 父推论全文(INDEX 摘要够用)
// - Reviewer 不读 INDEX, r2+ 不读全量旧审查档(改读 DED review_summary 紧凑摘要)
// - Revise 阶段自动将本轮裁决压进 DED review_summary(不靠 finalize 一次性填)
// - 每个 agent 上下文比 v1 少 30–50%

export const meta = {
  name: 'l4-pipeline',
  description: 'L4 复合推论管线 v2:author(INDEX+清单)→ adaptive 对抗审查 loop → 定论,轮间不过主循环',
  phases: [
    { title: 'Author',   detail: '读 INDEX+清单起草瘦身 candidate,父推论仅读摘要行' },
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
const l3Parents = b.l3Parents || []
const l4Parents = b.l4Parents || []
if (l3Parents.length < 2) {
  return { error: `l3Parents 至少需要 2 条 L3 推论作为主前提 (L4 硬门槛，当前 ${l3Parents.length} 条)` }
}

const DED_PATH = `${REPO}/L4-composites/corollaries/${b.id}-${b.slug}.yaml`
const REVIEW_PATH = `${REPO}/L4-composites/reviews/ADV-REVIEW-${b.reviewNum}-${b.id}.yaml`
const CHECKLIST = `${REPO}/docs/pipeline/l4-author-checklist.md`
const RUBRIC = `${REPO}/docs/pipeline/l4-review-rubric.md`
const L3_RUBRIC = `${REPO}/docs/pipeline/review-rubric.md`
const INDEX = `${REPO}/INDEX.md`
// 阅读包(v2.1):agent 冷启动只读 1 份而非 3-4 份,未命中输入成本 ↓25-40%
const AUTHOR_PACK = `${REPO}/docs/pipeline/author-pack.md`
const REVIEWER_PACK = `${REPO}/docs/pipeline/reviewer-pack.md`
const claimType = b.claimType || 'social_form_prediction'
const domain = JSON.stringify(b.domain || [])

// --- 结构化返回 schema(强制紧凑) ---
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
    validatorOk: { type: 'boolean' },
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
// brief.skipAuthor = true 时跳过作者阶段(L4 推论文件已在主循环外写好),直接进审查 loop。
// brief.freeDraft = true 时(实验性):先调免费模型出初稿,pro Author agent 编辑而非从零创作。
phase('Author')

// ── 可选:免费模型预草稿(实验性,freeDraft=true 时启用) ──
let draftNote = ''
if (b.freeDraft && !b.skipAuthor) {
  const briefJson = JSON.stringify(b).replace(/'/g, "'\\''")
  const draft = await agent(
    `Run free-model author draft (zero pro cost, experimental):
echo '${briefJson}' > /tmp/brief-${b.id}.json && cd ${REPO} && python scripts/author_draft.py --brief-file /tmp/brief-${b.id}.json
Read JSON from stdout. Return {done, draftPath, note} — just parse the JSON, no extra thinking.`,
    { label: `draft:${b.id}`, phase: 'Author', schema: REVISE_OUT }
  )
  if (draft && draft.done) {
    draftNote = `\n\n## ⚠️ 草稿已由免费模型预生成\n文件: ${DED_PATH}\n你的任务从"从零起草"变为"读草稿→修正遗漏→补全必填项→validate"。草稿必有遗漏(emergence_demonstration/2×2判空/L4专属字段),重点检查这些。`
    log(`free draft done: ${draft.draftPath || DED_PATH}`)
  } else {
    log(`free draft failed, Author 从零起草: ${draft ? draft.note : 'agent failed'}`)
  }
}

const authored = b.skipAuthor
  ? { done: true, coreOneLine: b.coreClaim || b.title, validatorOk: true }
  : await agent(
  `你是 L4 复合推论【作者${b.freeDraft ? '-编辑者' : ''}】,全新上下文。目标:${b.freeDraft ? '读免费模型的草稿,修正遗漏,补全必填项,产出合格的 candidate YAML' : '把下列 L4 复合推论写成一份【瘦身 canonical】的 candidate YAML'}。${draftNote}

## 封顶读取(阅读包+L4专属清单,不读 METHODOLOGY——清单已含规则 E/F/G)
1. 读 ${AUTHOR_PACK}(本体系的作者阅读包——含全部实体索引摘要+通用作者前置清单A-E段+瘦身格式)。读完这份,通用部分全覆盖。
2. 读 ${CHECKLIST}(L4 专属前置清单+瘦身格式)——逐条自查 L4 专属规则,L4 专属字段格式在底部。
3. L3 父推论 ${l3Parents.join(', ')} ——【仅读阅读包实体速览段摘要行,不逐份读全文】。
   起草中遇到具体歧义时再打开对应 L3 全文 (${REPO}/L3-deductions/corollaries/<id>-*.yaml)。
${l4Parents.length ? `4. L4 父推论同理,仅读 INDEX 摘要:${l4Parents.join(', ')}\n   全文在 ${REPO}/L4-composites/corollaries/<id>-*.yaml,遇歧义再打开。` : ''}

## 要写的 L4 复合推论
- id: ${b.id}   claim_type: ${claimType}   domain: ${domain}
- 主题: ${b.title}   核心一句话: ${b.coreClaim || '(从论点提炼)'}
- L3 父前提: ${l3Parents.join(', ')}${l4Parents.length ? `   L4 父前提: ${l4Parents.join(', ')}` : ''}
- 论点/承重逻辑/招牌预测:
${b.thesis}

## 硬要求
- 瘦身格式照清单底部节。L4 必填: deduction_form=composite / emergence_demonstration / depends_on.deductions=[${l3Parents.join(', ')}]${l4Parents.length ? ` / depends_on.composite_deductions=[${l4Parents.join(', ')}]` : ''}
- 涌现硬门槛:至少一个格子需 >=2 父推论合力,否则平凡合取。
- YAML 陷阱:多行段用 | 块标量,裸标量禁 ASCII 冒号+空格。
- 写到 ${DED_PATH};跑 \`cd ${REPO} && python scripts/validate.py\`,确认实体+1、无 ❌、L4 检查通过。

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
let roundVerdicts = []
let lastOneline = ''

while (round < MAX) {
  round++
  phase('Review')
  // v4.0: Review 段改用 MiniMax-M3 异血统承重墙（ICV 协议）。
  // Author=glm-5.2(智谱系) × Review=MiniMax-M3(minimax系) = 真正血统独立。
  // --layer L4 追加 L4 专属评分卡，workflow agent 只编排+报告。
  const reviewRel = REVIEW_PATH.replace(REPO + '/', '')
  const rev = await agent(
    `Run MiniMax-M3 adversarial review for ${b.id} round ${round} (异血统承重墙, ICV 协议, L4 专属评分卡):

cd ${REPO} && python scripts/review_minimax.py ${b.id} \\
  --review-round ${round} \\
  --review-path '${reviewRel}' \\
  --layer L4

Read JSON from stdout ({"done","validatorOk","verdict","requiredFixes":[...],"counterexample","oneline"}).
If done=false, report the note. Return only: {verdict, requiredFixes, counterexample, oneline, validatorOk}.`,
    { label: `review:${b.id}:r${round}`, phase: 'Review', schema: REVIEW_OUT }
  )
  if (!rev || rev.validatorOk === false) {
    return { id: b.id, verdict: 'review_failed', rounds: round, dedPath: DED_PATH,
             reviewPath: REVIEW_PATH, note: rev ? (rev.oneline || '审查档未过校验') : 'review agent 失败' }
  }

  verdict = (rev && rev.verdict) || 'needs_revision'
  fixes = (rev && rev.requiredFixes) || []
  lastCounterexample = (rev && rev.counterexample) || ''
  lastOneline = (rev && rev.oneline) || ''
  roundVerdicts.push({ n: round, v: verdict })
  log(`round ${round}: ${verdict}${fixes.length ? ` — ${fixes.length} fixes` : ''}`)

  if (verdict === 'verified' || verdict === 'rejected') break
  if (!fixes.length) { log(`round ${round}: needs_revision 但无 required,停(交主循环裁量)`); break }

  phase('Revise')
  // v3.0: 双厂商交叉验证(免费+免费=零成本质量门)
  const reviewRel = REVIEW_PATH.replace(REPO + '/', '')
  const fixesArg = fixes.map(f => f.replace(/'/g, "'\\''")).join(' ||| ')
  const revised = await agent(
    `Run flash revise for ${b.id} round ${round} (dual-provider cross-check, zero LLM cost):

cd ${REPO} && python scripts/flash_revise.py ${b.id} \\
  --cross-check \\
  --mode patch \\
  --fixes '${fixesArg}' \\
  --review-round ${round} \\
  --review-path '${reviewRel}'

Read the JSON result from stdout (it will be {"done": true/false, "validatorOk": true/false, "note": "..."}).
If flash_revise returns done=false, note the error in your return note field.
Return only the JSON: {done, validatorOk, note}.`,
    { label: `revise:${b.id}:r${round}`, phase: 'Revise', schema: REVISE_OUT }
  )
  if (!revised || !revised.validatorOk) {
    log(`round ${round}: 整改未过校验,停`)
    return { id: b.id, verdict: 'revise_failed', rounds: round, dedPath: DED_PATH, reviewPath: REVIEW_PATH }
  }
}

// ============ Phase 3: Finalize ============
if (verdict === 'verified') {
  phase('Finalize')
  const chain = roundVerdicts.map(r => `r${r.n} ${r.v}`).join(' -> ')
  const why = (lastOneline || '涌现成立,多父逐格判空,反例猎捕无活反例').replace(/'/g, "'\\''")
  const chainEsc = chain.replace(/'/g, "'\\''")
  const fin = await agent(
    `Run finalize for ${b.id} (scripted, zero LLM reasoning):
cd ${REPO} && python scripts/finalize.py ${b.id} \\
  --verdict verified \\
  --chain '${chainEsc}' \\
  --why '${why}' \\
  --review-num ${b.reviewNum}
Check stdout for ✅ validate 通过. Return {done, validatorOk, note}.`,
    { label: `finalize:${b.id}`, phase: 'Finalize', schema: REVISE_OUT }
  )
  if (!fin || !fin.validatorOk) {
    return { id: b.id, verdict: 'finalize_failed', rounds: round, dedPath: DED_PATH,
             reviewPath: REVIEW_PATH, note: fin ? fin.note : 'finalize 脚本失败' }
  }
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
