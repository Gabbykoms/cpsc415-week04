# Plan: Ask the course

**Status:** Approved by Gabriel Koomson in conversation after questioning the chunk size, overlap, and retrieval count. Approval preceded application code.

Implements [spec.md](spec.md) and the [approved intent](intent/ask-the-course.md).

## Files to create or change
| File | Purpose |
|---|---|
| `rag_common.py` | Shared configuration, API calls, corpus discovery and hashes, vector validation, index loading, and cosine similarity. |
| `indexer.py` | Split allowed Markdown files into chunks, embed them in batches, and atomically save an index. |
| `asker.py` | Retrieve and print chunks and scores, request a grounded answer, validate citation references, and support the no-retrieval baseline. |
| `eval.py` | Run the student's five questions in both modes and save results for human assessment. |
| `questions.json` | Gabriel's five questions, expected answers, expected sources, and purposes. |
| `results/` | Captured evaluation output and the separate stale-page experiment; never credentials. |
| `CHECKS.md` | Step proofs, human evaluation judgments, failures, and stale-page finding. |
| `README.md` | Setup, commands, configuration, questions, observations, and one explained line. |
| `.gitignore` | Ignore the generated `index.json` and temporary index files, in addition to secrets. |
| `CLAUDE.md` | Update commands and project conventions as implemented. |
| `plan.md` | Record Gabriel's questions, answers, corrections, and approval before code. |

## Order of work
Stop after each numbered step, show Gabriel its proof, and wait for his direction before proceeding to the next implementation step.

1. **Prepare repository and source documents.** Confirm this plan is questioned and approved; commit it as `Approve plan` before any code commit. Create the public GitHub repository from the course artifact-chain template and connect the local checkout, preserving the approved-intent/spec/plan history. Check the course checkout for changes, fetch updates, and fast-forward only if clean and compatible. If not, preserve local work and resolve the source version explicitly. Confirm the corpus includes weeks 01–03. Add index ignore rules. Confirm an API spending ceiling before paid calls.
2. **Build the indexer and shared utilities.** Read only the specified corpus paths; split each file into 250-word chunks with 50-word overlap. Store stable chunk IDs, source paths, text, and vectors. Embed batches of at most 32 chunks; validate counts, indices, dimensions, and finite nonzero vectors. Save metadata and hashes with the index atomically. Report file and chunk counts.
3. **Build the asker.** Check index metadata and source hashes before calling APIs. Embed the question with the same model, rank by cosine similarity, and select up to five chunks. Print their full text, paths, IDs, and scores. Ask MiniMax to answer with supporting citations or the specified refusal. Reject citation references not supplied in the prompt. Add no-retrieval mode without an embedding call or excerpts.
4. **Build and run the five-question evaluation.** Gabriel writes the five questions and expected answers before the run: three single-source, one requiring two pages, one unsupported. Implement the runner and save both modes' complete responses and retrieved chunks. Review answers against actual sources; record pass/fail with reasons and unavailable usage explicitly. Do not tune questions or silently discard failures to improve results.
5. **Investigate the stale page.** Ask: “Which Xiaomi MiMo model does this course use as the fallback or second model?” Inspect the answer and actual retrieved sources. Record conflicting statements, cited and misleading chunks, and a proposed way to prefer the current source. If the failure does not reproduce, report that honestly and still document the conflicting pages. Do not implement the optional fix.
6. **Explain and prepare submission.** Finish README and CHECKS, update conventions, and ask Gabriel to explain a ranking or refusal line. Inspect the diff for secrets and generated index files. Commit the completed work and create `week04-submitted` only after evaluation and documentation are complete. Push main and the tag; verify remote references and provide the repository URL for Gabriel's Moodle submission. Report unmet requirements honestly.

## Risks
- **Source freshness:** The initial local course clone lacks Week 3 pages. Indexing it prematurely would omit required evidence. A clean fast-forward must be confirmed; do not reset or overwrite local changes.
- **Chunk boundaries:** A 250-word chunk can separate a heading or policy from its details. The 50-word overlap mitigates but does not eliminate this. Inspect the five-question retrieval output before deciding whether a documented change is warranted.
- **Retrieval quality:** Similarity is not a correctness probability. Top-five retrieval may miss a needed page or return redundant overlapping chunks. Record source coverage, especially on the two-page question.
- **Contradictory pages:** Hash checks detect changes after indexing, not outdated text still present in the source repository. Similarity ranking does not know which page is current. Keep both pages for the stale-page experiment and document the outcome.
- **Grounding and citations:** A model can fabricate claims despite a grounding prompt, or cite a valid chunk that does not support its answer. Citation-ID checks cannot replace human semantic review.
- **API failures and cost:** Embedding or chat requests can fail or incur charges without useful output. No automatic retries; preserve an old index after a failed rebuild. Record usage when returned and stop paid work at the agreed spending limit.
- **Baseline interpretation:** With no excerpts and the same grounding instruction, refusing every question is legitimate. Describe this controlled comparison honestly rather than claiming it proves general model inability.
- **Publication:** Before pushing, inspect staged files for secrets. Do not publish API keys, local environment files, or the generated index.

## Proof
Record actual commands and observations in CHECKS.md as each step completes; all proofs below are planned, not executed.

1. `git log --oneline` shows `Approve plan` before implementation commits. `git status --short` and a corpus path listing establish the source checkout and required pages. Confirm no copied course pages in this project.
2. `python3 indexer.py` reports nonzero files and chunks and produces a loadable JSON index. Inspect source paths, metadata, overlap on adjacent chunks, and consistent vector dimensions. Manually verify cosine similarity on identical and orthogonal vectors. A missing course directory fails before a paid call. Verify a failed rebuild does not replace a valid index using a temporary output path.
3. `python3 asker.py "<a question supported by the indexed pages>"` prints at most five chunks in descending score order and a source-supported answer. An unsupported question produces the exact refusal. `--no-retrieval` reports that retrieval is disabled and supplies no chunks. Use temporary fixture files to check malformed-index, changed-source, and missing-key failures without modifying original course pages or revealing secrets. Capture actual errors; do not claim a model-dependent check passed in advance.
4. `python3 eval.py` runs the same five student-authored questions with and without retrieval, producing ten recorded outcomes. Review all ten against expected answers and source passages. CHECKS.md includes pass counts, failure reasons, and chunk sources for failures; any API error is an error, not a refusal or a pass.
5. `python3 asker.py "Which Xiaomi MiMo model does this course use as the fallback or second model?"` yields a captured response and retrieved chunks. CHECKS.md identifies conflicting text, what the model used, and one concrete mitigation such as explicit source-version metadata and a current-page precedence rule.
6. README commands match implemented CLI help. Gabriel explains one selected line in his own words. Inspect `git diff --cached` and tracked paths before publication. Verify the remote main branch and `week04-submitted` tag resolve to the intended commit. No Moodle submission is claimed unless actually performed.

## Student questions and plan corrections
Gabriel asked the following questions before approval:

1. **Why 50-word overlaps?** Repeating the last 50 words in the next chunk helps preserve context across boundaries. This is 20% overlap, not a guarantee that complete sentences or sections stay together. Clarification: inspect boundary-related retrieval failures before changing the overlap, and record any change.
2. **Why 250-word chunks?** This is an initial compromise between enough context for a policy or explanation and a focused embedding. Larger chunks can dilute relevance; smaller chunks can omit necessary context. Clarification: the size is a starting hypothesis, not an experimentally established optimum.
3. **Why five relevant chunks for the asker?** Multiple passages can support questions spanning two pages. More passages add cost and possible distractions; fewer may omit evidence. Overlapping passages can crowd out other sources. Clarification: inspect source coverage in the five-question evaluation and document any adjustment rather than assuming five is optimal.

Gabriel then said “let's move on,” approving progression after these answers. The initial parameters remain 250 words, 50 words overlap, and five retrieved chunks; the clarifications above explain their tradeoffs and how evaluation will assess them.

## Subagents and parallel work
None. This small introductory lab will be implemented sequentially, with proof shown after each step. No worktrees, feature branches, or pull requests.

**Approved by:** Gabriel Koomson, October 19, 2026, in conversation after the questions above.
