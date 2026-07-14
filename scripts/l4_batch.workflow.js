// scripts/l4_batch.workflow.js
// L4 批量复合推论:pipeline 并行跑 N 条 l4-pipeline 推论,各自独立走完整对抗审查
// (author→审查loop→revise→finalize),互不阻塞。墙钟 ≈ 单条最慢链,而非 N 倍。
// 每条重产物留在各自子链,主循环只收每条一行紧凑裁决。
//
// 调用:
//   小批量(≤3条):Workflow({ scriptPath, args: { briefs: [BRIEF, ...] } })
//   大批量(>3条,防 args 串化截断):先把 briefs 写成 JSON 文件,传 { briefsFile: '<绝对路径>' }
// 每个 BRIEF 格式见 l4_pipeline.workflow.js 顶部(id/slug/reviewNum/title/thesis/coreClaim/l3Parents/claimType/domain)。

export const meta = {
  name: 'l4-batch',
  description: '批量 L4 复合推论:pipeline 并行跑 N 条,各走 author→对抗审查loop→finalize,只回每条紧凑裁决',
  phases: [
    { title: 'Load',  detail: '从文件读 briefs(大批量模式)或从 args 直取(小批量模式)' },
    { title: 'Batch', detail: 'N 条 L4 推论并行起跑,各自独立生命周期,互不阻塞' },
  ],
}

let a = args || {}
if (typeof a === 'string') {
  try { a = JSON.parse(a) } catch (e) {
    return { error: 'args 是字符串但非合法 JSON', raw: String(a).slice(0, 200) }
  }
}
const REPO = a.repo || '/home/hq/research/human-society'
const L4_PIPELINE = `${REPO}/scripts/l4_pipeline.workflow.js`

// --- briefs 来源:优先从 briefsFile 读(防大 args 串化截断),否则从 args.briefs/args 数组取 ---
let briefs = []
if (a.briefsFile) {
  phase('Load')
  const loaded = await agent(
    `用 Read 工具读文件 ${a.briefsFile},把内容作为 JSON 解析,返回 { briefs: [...] }。每个 brief 原样保留所有字段。`,
    { label: 'load-briefs', phase: 'Load', schema: { type: 'object', properties: { briefs: { type: 'array' } }, required: ['briefs'] }, agentType: 'general-purpose' }
  )
  briefs = (loaded && loaded.briefs) ? loaded.briefs : []
  if (!briefs.length) {
    return { error: '从 briefsFile 读到的 briefs 为空或解析失败', file: a.briefsFile }
  }
  log(`从文件读入 ${briefs.length} 条 L4 briefs`)
} else {
  briefs = Array.isArray(a) ? a : (a.briefs || [])
}

if (!Array.isArray(briefs) || briefs.length === 0) {
  return { error: '未提供 briefs:传 { briefs: [...] } 或 { briefsFile: "<path>" }', got: typeof briefs }
}

// 基本校验:每条 brief 必须有 l3Parents(≥2)
const invalid = briefs.filter((b) => !b.l3Parents || b.l3Parents.length < 2)
if (invalid.length) {
  return { error: `${invalid.length} 条 brief 的 l3Parents 不足 2 条(L4 硬门槛)`, ids: invalid.map((b) => b.id) }
}

log(`批量起跑 ${briefs.length} 条 L4 推论:${briefs.map((b) => b.id).join(', ')}`)

phase('Batch')
const results = await parallel(
  briefs.map((brief) => () => workflow({ scriptPath: L4_PIPELINE }, brief))
)

const summary = results.map((r, i) => {
  const id = (briefs[i] && briefs[i].id) || `#${i}`
  if (!r) return { id, verdict: 'workflow_failed' }
  return {
    id: r.id || id, verdict: r.verdict, rounds: r.rounds, core: r.core,
    counterexample: r.counterexample, dedPath: r.dedPath, reviewPath: r.reviewPath,
  }
})

const verified = summary.filter((s) => s.verdict === 'verified').map((s) => s.id)
const other = summary.filter((s) => s.verdict !== 'verified')

return {
  batch: briefs.length,
  verified,
  needsAttention: other,
  all: summary,
  next: verified.length
    ? `主循环:${verified.join('/')} 已 verified 且过校验,git add 各自两文件并提交(按授权自主提交);其余(${other.map((s) => s.id + ':' + s.verdict).join(', ') || '无'})上报`
    : '主循环:无 verified,逐条上报',
}
