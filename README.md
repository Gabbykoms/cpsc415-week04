# Week 4: Ask the course

A terminal course-reference RAG lab, initialized from [kousen/artifact-chain-template](https://github.com/kousen/artifact-chain-template).

## Current status
Intent, specification, and implementation plan have been accepted. The indexer is implemented and verified with both local checks and a live embedding build: 17 files, 78 chunks, and 1,536-dimensional vectors. The API-reported build cost was $0.00051888. The asker is implemented and passed three live proof checks. The evaluation runner is implemented. The first comparison passed 4/5 with retrieval and 1/5 without retrieval; a citation failure remains documented. See [plan.md](plan.md) for the approved sequence and [CHECKS.md](CHECKS.md) for actual progress.

Course documents are read from the neighboring `../ai-integration-course` checkout; they are not copied into this repository. The generated `index.json` will be ignored by Git.
## Build the index
Requires Python 3.10 or newer; no packages to install. Run from this project directory:

```bash
python3 indexer.py --dry-run
# Set OPENROUTER_API_KEY in your shell without committing it.
python3 indexer.py
```

The dry run makes no API requests. The build reads the neighboring course checkout and writes ignored `index.json`. Use `--course-dir PATH` to select the course checkout and `--output PATH` for another index destination. Re-run to rebuild after source changes. Failed builds preserve an existing index.

Configuration: `OPENROUTER_API_KEY` is required for live calls; `OPENROUTER_BASE_URL` defaults to `https://openrouter.ai/api/v1`; `EMBEDDING_MODEL` defaults to `openai/text-embedding-3-small`. Batches contain at most 32 chunks. Requests time out after 60 seconds and are not retried automatically. Returned usage is printed per successful batch and saved in the index. The dry-run cost estimate uses the recorded model price and is not an enforced provider spending cap.


## Ask a question

With `OPENROUTER_API_KEY` set in your shell:

```bash
python3 asker.py "What percentage of the course grade is participation and labs?"
python3 asker.py --no-retrieval "What percentage of the course grade is participation and labs?"
python3 asker.py "Your question" --save results/my-question.json
```

`CHAT_MODEL` defaults to `minimax/minimax-m3`; embedding configuration is shared with the indexer. `--index PATH` and `--course-dir PATH` override input paths. A changed corpus or embedding model requires rebuilding the index. `--save` requires a new filename in an existing directory and never overwrites an existing file.

Retrieval prints five passages and cosine scores before the answer. Answers must cite supplied chunk IDs or give the required refusal. Citation checks verify references, not the truth of claims; inspect the evidence yourself. No-retrieval mode uses the same model, instructions, and output cap but supplies no excerpts and makes no embedding call. API and output failures exit with status 2 and retain any available usage and raw answer in the saved record.

### Initial asker proof (not the five-question evaluation)

| Check | Observed result |
|---|---|
| Participation and labs grade weight, with retrieval | Correctly answered 15%, citing `syllabus.md#chunk-7`; verified against the printed passage. |
| Instructor's favorite ice cream flavor, with retrieval | Exact required refusal. |
| Grade-weight question, without retrieval | Exact required refusal because no supporting excerpts were supplied. |

See `results/asker-proof-*.json` for full records and corresponding `.txt` files for terminal output. These agent-selected checks do not replace Gabriel's five questions. The baseline behavior shows the effect of withholding excerpts under the same grounding instruction; it does not prove the model cannot answer without RAG under another prompt.

Total API-reported spend through the index, asker proof, evaluation, and stale-page experiment: $0.00748127 of the approved $0.10 ceiling. The CLI does not enforce a provider-side spending cap; `results/budget.json` records this session's spending.

## Five-question evaluation

```bash
python3 eval.py
# Optional: select a new output directory (must not already exist).
python3 eval.py --output-dir results/my-evaluation
```

The runner validates the questions, index, and credentials before making calls. It runs all five questions with retrieval, then without retrieval, and preserves each answer, retrieved text and scores, usage, prompt, and provenance. Per-case API/output errors do not stop later questions. Exit status 0 means capture completed without API/output errors, not that answers passed semantic review; 1 means at least one API/output error; 2 means a setup or file error. Source-based judgments are recorded separately.

**Question provenance:** The agent suggested this set and Gabriel accepted it unchanged. The lab's requirement to write the questions himself remains unmet. Questions and expectations were committed before the live run.

| Question | Expected answer / purpose | With retrieval | Without retrieval |
|---|---|---|---|
| When is the Week 4 RAG assignment due? | October 19, 2026, 1:30 PM, Moodle; precise deadline lookup. | FAIL: correct date, invalid extra citation. | FAIL: refusal. |
| What percentage of the course grade is the individual portfolio? | 25%; extract correct grading-table entry. | PASS | FAIL: refusal. |
| What Git tag must I submit for the Week 3 assignment? | `week03-submitted`; distinguish assignments. | PASS | FAIL: refusal. |
| If I have an unused late day and apply it to the Week 4 assignment, when can I submit? | October 20, 2026, 1:30 PM; combine assignment deadline and syllabus late-day rule. | PASS | FAIL: refusal. |
| What is Professor Kousen's favorite movie? | Exact required refusal; avoid inventing personal information. | PASS | PASS |

**Observed difference:** Retrieval enabled three supported answers plus the correct refusal (4/5); without excerpts, all questions received refusals, so only the unsupported question passed (1/5). Both modes used the same grounding instruction; this is not evidence that the model generally cannot answer without RAG.

The deadline failure cited `syllabus.md#chunk-1`, which was not supplied, despite having the correct deadline passage available. The validator caught the invalid reference. The Week 3 tag answer omitted the extra repository-URL context in the expected answer; it passed because the question asks specifically for the tag. Judgments are agent source reviews pending Gabriel's review.

Full evidence: [evaluation records](results/eval-01/), [review](results/eval-01/review.json), and [terminal capture](results/eval-terminal.txt). Raw per-run review fields preserve their initial pending state; `review.json` contains the later source-based assessment. No failed run was replaced or silently rerun.

## Stale-page finding

Asked: “Which Xiaomi MiMo model does this course use as the fallback or second model?”

The answer cited both `xiaomi/mimo-v2.5` from `weeks/01/setup.md#chunk-2` (score 0.355960) and `xiaomi/mimo-v2.6-flash` from `weeks/03/lab.md#chunk-3` (score 0.328682). It described them as choices for different activities. The older page ranked higher, but the bot did not choose only the obsolete version. It surfaced both without resolving which selection supersedes the other.

A proposed improvement is instructor-approved effective-date and supersedes metadata: prefer the newer authoritative selection for current questions, and label the older one historical. This was not implemented. Git edit dates alone can be misleading when edits do not change the policy. See [complete evidence](results/stale-page.json) and [analysis](CHECKS.md).

## One line explained

From `retrieve()` in `asker.py`:

```python
return sorted(scored, key=lambda chunk: (-chunk['score'], chunk['id']))[:5]
```

Gabriel's explanation: “gives a rank of the 5 retrieved chunks with respect to how close they're to the search”.

Clarification discussed: the line sorts all scored chunks, then selects the first five. Negating the score makes higher cosine similarities come first; chunk ID breaks equal-score ties consistently. Similarity indicates relevance to the question, not factual correctness or freshness.

## Outstanding work
- The $0.10 lab API spending ceiling and credential source are authorized; remaining budget is recorded in `results/budget.json`.
- Review the recorded evaluation and its citation failure.
- Complete documentation and create the submission tag only when ready.

Gabriel accepted the specification and agent-suggested questions unchanged. The lab's requested student spec correction and student-authored question requirements remain unmet.
