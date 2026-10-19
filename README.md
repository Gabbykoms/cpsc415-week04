# Week 4: Ask the course

A terminal course-reference RAG lab, initialized from [kousen/artifact-chain-template](https://github.com/kousen/artifact-chain-template).

## Current status
Intent, specification, and implementation plan have been accepted. The indexer is implemented and locally checked with simulated API responses; a live embedding build is pending credential authorization. The asker and evaluation runner are not implemented yet. See [plan.md](plan.md) for the approved sequence and [CHECKS.md](CHECKS.md) for actual progress.

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


## Outstanding work
- The $0.10 lab API spending ceiling is approved; authorize the credential source before the live build.
- Complete live indexer verification, then implement the asker, showing proof after each plan step.
- Gabriel supplies five evaluation questions; run them with and without retrieval.
- Record the stale-page experiment and explain one code line.
- Complete documentation and create the submission tag only when ready.

Gabriel accepted the specification unchanged. The lab's requested student spec correction remains unmet.
