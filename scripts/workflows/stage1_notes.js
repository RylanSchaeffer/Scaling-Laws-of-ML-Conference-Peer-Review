export const meta = {
  name: 'neurips2021-stage1-notes',
  description: 'Stage 1: one agent per pair writes structured notes on why the two NeurIPS 2021 committees disagreed',
  phases: [{ title: 'Notes' }],
}
// args: { pairs: ["n21-002", ...] }  at most 8 per workflow (the concurrency cap on this machine), so every agent runs at once
const ROOT = '/Users/rylanschaeffer/Documents/Scaling-Laws-of-ML-Conference-Peer-Review/data/paired_reviews/neurips2021'
const SCHEMA = { type: 'object', properties: {
  pair_id: { type: 'string' }, wrote_json: { type: 'boolean' }, wrote_md: { type: 'boolean' },
  verdict_first_sentence: { type: 'string' }, confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  read_pdf: { type: 'boolean' } }, required: ['pair_id', 'wrote_json', 'wrote_md', 'verdict_first_sentence', 'confidence', 'read_pdf'] }
const prompt = (id) => `You are one analyst in a study of the NeurIPS 2021 consistency experiment. Your pair is ${id}.

1. Read the instructions in ${ROOT}/analysis/stage1/prompt.md in full. They define exactly what to read and what to write.
2. The pair's files are in ${ROOT}/pairs/${id}/ : paper.json (title, kind of discrepancy, final decision), pair.md (both committees' complete records), a/decision.json and b/decision.json (each committee's own decision), a/reviews.jsonl, b/reviews.jsonl, a/discussion.jsonl, b/discussion.jsonl, and a/paper.pdf (the submission; the same PDF is under b/).
3. Fill the placeholders of the instructions from those files: {pair_dir} = ${ROOT}/pairs/${id}, {pair_id} = ${id}, {own_a} and {own_b} from the two decision.json files, {final} and {kind} from paper.json, {out_json} = ${ROOT}/analysis/stage1/${id}.json, {out_md} = ${ROOT}/analysis/stage1/${id}.md.
4. Write exactly those two files. Do not edit any other file. Do not run any script that modifies the dataset.

Read the whole of pair.md before judging anything; it is long. Open the PDF when a reviewer makes a specific, checkable claim about the paper and the discrepancy turns on it. Your final text answer is only the small JSON summary requested by the schema; the substance goes in the two files.`
phase('Notes')
const pairs = args.pairs
if (pairs.length > 8) throw new Error('at most 8 pairs per workflow')
const out = await parallel(pairs.map(id => () => agent(prompt(id), { label: `notes:${id}`, phase: 'Notes', schema: SCHEMA, model: 'opus', effort: 'max' })
  .then(r => r || { pair_id: id, wrote_json: false, wrote_md: false, verdict_first_sentence: 'agent returned nothing', confidence: 'low', read_pdf: false })))
return out
