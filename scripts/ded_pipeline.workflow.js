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
// 阅读包(v2.1):agent 冷启动只读 1 份而非 3-4 份,未命中输入成本 ↓25-40%
const AUTHOR_PACK = `${REPO}/docs/pipeline/author-pack.md`
const REVIEWER_PACK = `${REPO}/docs/pipeline/reviewer-pack.md`
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
// brief.skipAuthor = true 时跳过作者阶段(推论文件已在主循环外写好),直接进审查 loop。
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
    draftNote = `\n\n## ⚠️ 草稿已由免费模型预生成\n文件: ${DED_PATH}\n你的任务从"从零起草"变为"读草稿→修正遗漏→补全必填项→validate"。草稿必有遗漏(primary_suspect/2×2判空/confidence标注),重点检查这些。`
    log(`free draft done: ${draft.draftPath || DED_PATH}`)
  } else {
    log(`free draft failed, Author 从零起草: ${draft ? draft.note : 'agent failed'}`)
  }
}

const authored = b.skipAuthor
  ? { done: true, coreOneLine: b.coreClaim || b.title, validatorOk: true }
  : await agent(
  `你是公理化推论【作者${b.freeDraft ? '-编辑者' : ''}】,全新上下文。目标:${b.freeDraft ? '读免费模型的草稿,修正遗漏,补全必填项,产出合格的 candidate YAML' : '把下列推论写成一份【瘦身 canonical】的 candidate YAML'}。${draftNote}

## 封顶读取(一份阅读包,预编了实体速览+前置清单+瘦身格式)
1. 读 ${AUTHOR_PACK}(本体系的作者阅读包——含全部实体索引摘要+作者前置清单A-E段+瘦身canonical格式)。读完这份就够了,不用分别读INDEX+checklist。
2. 承重砖 ${bricks} ——阅读包的实体速览段已含各砖摘要行。起草中遇到具体歧义时再打开对应砖全文 (${REPO}/L2-bridging/verified/<id>-*.yaml)。

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
log(b.skipAuthor ? `author skipped (pre-authored): ${authored.coreOneLine}` : `author done: ${authored.coreOneLine}`)

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
  // workflow agent 只编排+报告，审查推理由 review_minimax.py 调 MiniMax-M3 完成。
  const reviewRel = REVIEW_PATH.replace(REPO + '/', '')
  const rev = await agent(
    `Run MiniMax-M3 adversarial review for ${b.id} round ${round} (异血统承重墙, ICV 协议):

cd ${REPO} && python scripts/review_minimax.py ${b.id} \\
  --review-round ${round} \\
  --review-path '${reviewRel}' \\
  --layer L3

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
  // sensenova(deepseek-v4-flash) + zhipu(glm-4-flash) 独立血统同时跑
  // 两家都过且 YAML 一致→高置信;有差异→保留 sensenova,报告差异量
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
  const why = (lastOneline || '核心载重成立,反例猎捕无活反例').replace(/'/g, "'\\''")
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
