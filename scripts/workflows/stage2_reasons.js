export const meta = {
  name: 'neurips2021-stage2-reasons',
  description: 'Stage 2: grow the set of reasons one pair at a time from the stage 1 notes, every turn logged',
  phases: [{ title: 'Pass' }, { title: 'Back-fill' }, { title: 'Merge' }],
}
// args: { run: 1, order: ["n21-002", ...], start_turn: 1 }
// The set of reasons lives on disk at analysis/stage2/run_<run>/reasons.json and is updated by each turn's agent; the
// script passes it forward only through the file. Turns are sequential. Back-fill is parallel per pair (8 at once).
const ROOT = '/Users/rylanschaeffer/Documents/Scaling-Laws-of-ML-Conference-Peer-Review/data/paired_reviews/neurips2021'
const RUN = `${ROOT}/analysis/stage2/run_${args.run}`
const TURN = { type: 'object', properties: { pair_id: { type: 'string' }, applied: { type: 'array', items: { type: 'string' } },
  added: { type: 'array', items: { type: 'string' } }, n_reasons_after: { type: 'integer' }, wrote_turn_file: { type: 'boolean' } },
  required: ['pair_id', 'applied', 'added', 'n_reasons_after', 'wrote_turn_file'] }
const BF = { type: 'object', properties: { pair_id: { type: 'string' }, judged: { type: 'integer' }, yes: { type: 'array', items: { type: 'string' } }, wrote_file: { type: 'boolean' } },
  required: ['pair_id', 'judged', 'yes', 'wrote_file'] }
const MERGE = { type: 'object', properties: { merges: { type: 'array', items: { type: 'object', properties: { keep: { type: 'string' }, absorb: { type: 'string' }, why: { type: 'string' } }, required: ['keep', 'absorb', 'why'] } }, wrote_file: { type: 'boolean' } }, required: ['merges', 'wrote_file'] }

const turnPrompt = (n, id) => `You are the stage 2 judge of a study of why two NeurIPS 2021 committees disagreed about the same paper. Read ${ROOT}/analysis/stage2/prompt.md in full first; it defines the task, the file formats and the rules.
This is turn ${n} of run ${args.run}. The pair is ${id}. Its stage 1 notes are ${ROOT}/analysis/stage1/${id}.json and ${id}.md; the pair's own records are under ${ROOT}/pairs/${id}/ if you need to check something.
The current set of reasons is ${RUN}/reasons.json (create it as an empty list if it does not exist). Judge which reasons apply to this pair and which new reasons it needs, then write ${RUN}/turn_${String(n).padStart(3, '0')}.json and update ${RUN}/reasons.json exactly as the instructions say. Edit no other file.`
const bfPrompt = (id, n) => `You are the back-fill judge of stage 2 (read ${ROOT}/analysis/stage2/prompt.md, section "Back-fill"). Run ${args.run}. The pair is ${id}, processed at turn ${n}. The final set of reasons is ${RUN}/reasons.json; the reasons created after turn ${n} were never judged for this pair. Read the pair's stage 1 notes (${ROOT}/analysis/stage1/${id}.json and .md), judge each of those later reasons for this pair, yes or no with one line of justification, and write ${RUN}/backfill_${id}.json. Create no reasons; edit no other file.`
const mergePrompt = `You are the merge judge of stage 2 (read ${ROOT}/analysis/stage2/prompt.md, section "Merge"). Run ${args.run}. Read ${RUN}/reasons.json and name every pair of entries that are one reason under two names. Write ${RUN}/merges.json as the instructions say. Change nothing else.`

const order = args.order
const start = args.start_turn || 1
phase('Pass')
const turns = []
for (let i = start - 1; i < order.length; i++) {
  const n = i + 1
  const r = await agent(turnPrompt(n, order[i]), { label: `turn ${n}: ${order[i]}`, phase: 'Pass', schema: TURN, model: 'opus', effort: 'max' })
  turns.push(r || { pair_id: order[i], applied: [], added: [], n_reasons_after: -1, wrote_turn_file: false })
  if (n % 10 === 0) log(`turn ${n}/${order.length}: ${turns[turns.length - 1].n_reasons_after} reasons`)
}
phase('Back-fill')
const bf = await parallel(order.map((id, i) => () => agent(bfPrompt(id, i + 1), { label: `backfill:${id}`, phase: 'Back-fill', schema: BF, model: 'opus', effort: 'max' })))
phase('Merge')
const merges = await agent(mergePrompt, { label: 'merge', phase: 'Merge', schema: MERGE, model: 'opus', effort: 'max' })
return { turns: turns.length, failed_turns: turns.filter(t => !t.wrote_turn_file).map(t => t.pair_id), backfilled: bf.filter(Boolean).length, merges: merges && merges.merges }
