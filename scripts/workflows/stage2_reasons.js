export const meta = {
  name: 'neurips2021-stage2-reasons',
  description: 'Stage 2: grow the set of reasons from the stage 1 notes, every judgement logged on disk',
  phases: [{ title: 'Pass' }, { title: 'Blocks' }, { title: 'Back-fill' }, { title: 'Merge' }],
}
// args: { run: 1, mode: 'pass' | 'blocks' | 'backfill' | 'merge', order: [...all 301 pair ids in order...],
//         start_turn, end_turn (pass, blocks; 1-based, inclusive), block_size (blocks), pairs: [...] (backfill) }
// The set of reasons lives on disk at analysis/stage2/run_<run>/reasons.json; the script passes state only through files.
// mode 'pass': one turn at a time; the turn's agent appends its new reasons to reasons.json itself.
// mode 'blocks': block_size pairs judged at once against the same frozen set; each proposes reasons in its turn file and
//   touches reasons.json not at all; one consolidation agent per block maps proposals to existing reasons or appends
//   new ones and writes block_<bbb>.json. Back-fill later judges, for each pair, every reason its turn did not judge.
const ROOT = '/Users/rylanschaeffer/Documents/Scaling-Laws-of-ML-Conference-Peer-Review/data/paired_reviews/neurips2021'
const RUN = `${ROOT}/analysis/stage2/run_${args.run}`
const OPTS = { model: 'opus', effort: 'max' }
const pad = (n) => String(n).padStart(3, '0')
const TURN = { type: 'object', properties: { pair_id: { type: 'string' }, applied: { type: 'array', items: { type: 'string' } },
  added: { type: 'array', items: { type: 'string' } }, n_reasons_after: { type: 'integer' }, wrote_turn_file: { type: 'boolean' } },
  required: ['pair_id', 'applied', 'added', 'n_reasons_after', 'wrote_turn_file'] }
const BLOCK = { type: 'object', properties: { block: { type: 'integer' }, proposals: { type: 'integer' }, mapped_existing: { type: 'integer' },
  merged_within_block: { type: 'integer' }, new_reasons: { type: 'array', items: { type: 'string' } }, n_reasons_after: { type: 'integer' }, wrote_file: { type: 'boolean' } },
  required: ['block', 'proposals', 'mapped_existing', 'merged_within_block', 'new_reasons', 'n_reasons_after', 'wrote_file'] }
const BF = { type: 'object', properties: { pair_id: { type: 'string' }, judged: { type: 'integer' }, yes: { type: 'array', items: { type: 'string' } }, wrote_file: { type: 'boolean' } },
  required: ['pair_id', 'judged', 'yes', 'wrote_file'] }
const MERGE = { type: 'object', properties: { merges: { type: 'array', items: { type: 'object', properties: { keep: { type: 'string' }, absorb: { type: 'string' }, why: { type: 'string' } }, required: ['keep', 'absorb', 'why'] } }, wrote_file: { type: 'boolean' } }, required: ['merges', 'wrote_file'] }

const common = (n, id) => `You are a stage 2 judge in a study of why two NeurIPS 2021 committees disagreed about the same paper. Read ${ROOT}/analysis/stage2/prompt.md in full first; it defines the task, the file formats and the rules.
Run ${args.run}, turn ${n}. The pair is ${id}. Its stage 1 notes are ${ROOT}/analysis/stage1/${id}.json and ${ROOT}/analysis/stage1/${id}.md; the pair's own records are under ${ROOT}/pairs/${id}/ if you need to check something.
The current set of reasons is ${RUN}/reasons.json (treat a missing file as an empty list).`
const passPrompt = (n, id) => `${common(n, id)}
This is a SEQUENTIAL turn (prompt section "A turn"). Judge which reasons apply to this pair and which new reasons it needs, write ${RUN}/turn_${pad(n)}.json, and append your new reasons to ${RUN}/reasons.json exactly as the instructions say. Edit no other file.`
const blockPrompt = (n, id, b) => `${common(n, id)}
This is a BLOCK turn (prompt section "A block turn"), block ${b}. Judge which reasons apply to this pair; where none fits, PROPOSE new reasons in your turn file with ids "P1", "P2", ... Write ${RUN}/turn_${pad(n)}.json. Do NOT write to ${RUN}/reasons.json; a consolidation step appends new reasons after the block. Edit no other file.`
const consolidatePrompt = (b, turns) => `You are the consolidation judge of stage 2 (read ${ROOT}/analysis/stage2/prompt.md, section "Consolidation"). Run ${args.run}, block ${b}. The block's turn files are: ${turns.map(n => `${RUN}/turn_${pad(n)}.json`).join(', ')}. The current set of reasons is ${RUN}/reasons.json.
For every proposal in those files' "added" lists decide: it is an existing reason under another name (map to it); it is the same new mechanism as another proposal in this block (one new reason for all of them); or it is new on its own. Append the new reasons to ${RUN}/reasons.json with the next ids, and write ${RUN}/block_${pad(b)}.json exactly as the instructions say. Edit no other file.`
const bfPrompt = (id, n) => `You are the back-fill judge of stage 2 (read ${ROOT}/analysis/stage2/prompt.md, section "Back-fill"). Run ${args.run}. The pair is ${id}, judged at turn ${n} (${RUN}/turn_${pad(n)}.json). The final set of reasons is ${RUN}/reasons.json. Every reason in it whose id does not appear in that turn file's "judgements" was never judged for this pair. Read the pair's stage 1 notes (${ROOT}/analysis/stage1/${id}.json and ${ROOT}/analysis/stage1/${id}.md), judge each such reason for this pair, yes or no with one line of justification, and write ${RUN}/backfill_${id}.json. Create no reasons; edit no other file.`
const mergePrompt = `You are the merge judge of stage 2 (read ${ROOT}/analysis/stage2/prompt.md, section "Merge"). Run ${args.run}. Read ${RUN}/reasons.json and name every pair of entries that are one mechanism under two names. Write ${RUN}/merges.json as the instructions say. Change nothing else.`

const order = args.order
const mode = args.mode || 'pass'
if (mode === 'pass') {
  phase('Pass')
  const start = args.start_turn || 1, end = args.end_turn || order.length
  const turns = []
  for (let n = start; n <= end; n++) {
    const id = order[n - 1]
    const r = await agent(passPrompt(n, id), { label: `turn ${n}: ${id}`, phase: 'Pass', schema: TURN, ...OPTS })
    turns.push(r || { pair_id: id, applied: [], added: [], n_reasons_after: -1, wrote_turn_file: false })
    log(`turn ${n}: ${id} applied ${turns[turns.length - 1].applied.length}, added ${turns[turns.length - 1].added.length}, set ${turns[turns.length - 1].n_reasons_after}`)
  }
  return { mode, turns: turns.map(t => ({ pair_id: t.pair_id, applied: t.applied.length, added: t.added, n_after: t.n_reasons_after })), failed: turns.filter(t => !t.wrote_turn_file).map(t => t.pair_id) }
}
if (mode === 'blocks') {
  phase('Blocks')
  const start = args.start_turn, end = args.end_turn, k = args.block_size || 8
  const out = []
  for (let s = start; s <= end; s += k) {
    const ns = []
    for (let n = s; n <= Math.min(s + k - 1, end); n++) ns.push(n)
    const b = Math.floor((s - 1) / k) + 1
    const rs = await parallel(ns.map(n => () => agent(blockPrompt(n, order[n - 1], b), { label: `turn ${n}: ${order[n - 1]}`, phase: 'Blocks', schema: TURN, ...OPTS })))
    const failed = ns.filter((n, i) => !rs[i] || !rs[i].wrote_turn_file)
    const okTurns = ns.filter((n, i) => rs[i] && rs[i].wrote_turn_file)
    const proposals = rs.filter(Boolean).reduce((a, r) => a + r.added.length, 0)
    let c = null
    if (okTurns.length) c = await agent(consolidatePrompt(b, okTurns), { label: `consolidate block ${b}`, phase: 'Blocks', schema: BLOCK, ...OPTS })
    out.push({ block: b, turns: ns, failed, proposals, consolidated: !!(c && c.wrote_file), new_reasons: c ? c.new_reasons : [], n_after: c ? c.n_reasons_after : -1 })
    log(`block ${b} (turns ${ns[0]}-${ns[ns.length - 1]}): ${proposals} proposals, ${c ? c.new_reasons.length : '?'} new, set ${c ? c.n_reasons_after : '?'}${failed.length ? `, FAILED turns ${failed.join(',')}` : ''}`)
  }
  return { mode, blocks: out }
}
if (mode === 'backfill') {
  phase('Back-fill')
  const pairs = args.pairs
  const rs = await parallel(pairs.map(id => () => agent(bfPrompt(id, order.indexOf(id) + 1), { label: `backfill:${id}`, phase: 'Back-fill', schema: BF, ...OPTS })))
  return { mode, done: rs.filter(r => r && r.wrote_file).map(r => r.pair_id), failed: pairs.filter((id, i) => !rs[i] || !rs[i].wrote_file) }
}
if (mode === 'merge') {
  phase('Merge')
  const m = await agent(mergePrompt, { label: 'merge', phase: 'Merge', schema: MERGE, ...OPTS })
  return { mode, merges: m && m.merges, wrote: !!(m && m.wrote_file) }
}
throw new Error(`unknown mode ${mode}`)
