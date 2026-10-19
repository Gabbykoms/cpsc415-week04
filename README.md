# Week 4: Ask the course

A terminal course-reference RAG lab, initialized from [kousen/artifact-chain-template](https://github.com/kousen/artifact-chain-template).

## Current status
Intent, specification, and implementation plan have been accepted. The indexer is implemented and verified with both local checks and a live embedding build: 17 files, 78 chunks, and 1,536-dimensional vectors. The API-reported build cost was $0.00051888. The asker is implemented and passed three live proof checks. The five-question evaluation runner is not implemented yet. See [plan.md](plan.md) for the approved sequence and [CHECKS.md](CHECKS.md) for actual progress.

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

Total API-reported spend through these checks: $0.00201516 of the approved $0.10 ceiling. The CLI does not enforce a provider-side spending cap; `results/budget.json` records this session's spending.

## Outstanding work
- The $0.10 lab API spending ceiling and credential source are authorized; remaining budget is recorded in `results/budget.json`.
- Review the completed asker proof, then proceed to the five-question evaluation.
- Gabriel supplies five evaluation questions; run them with and without retrieval.
- Record the stale-page experiment and explain one code line.
- Complete documentation and create the submission tag only when ready.

Gabriel accepted the specification unchanged. The lab's requested student spec correction remains unmet.
