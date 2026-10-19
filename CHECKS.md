# Checks: Ask the course

## Step 1: Repository and source preparation

- Intent committed: `b76966a` (`Approve Ask-the-course intent`).
- Specification committed: `4d6df96` (`Approve spec`). Accepted unchanged; the student correction requirement remains unmet.
- Plan committed: `f997855` (`Approve plan`), after Gabriel asked about chunk size, overlap, and retrieval count. No application code existed at approval.
- Local project initialized by cloning the course artifact-chain template. Upstream template remote removed to avoid accidental pushes to it.
- Course repository updated by clean fast-forward from `be507a2` to `5445682`. `git status --short` was empty afterward.
- Allowed corpus contains 17 Markdown files: syllabus (1), assignments (7), and weeks 01–03 (9). Includes the assignments directory as specified, even where assignment filenames mention later weeks; weeks/04 and weeks/05 directories are excluded.
- Course files remain in the neighboring checkout. No course pages copied into this project.
- `.gitignore` excludes `index.json` and its temporary variants, alongside existing secret/environment patterns.
- No paid API calls made. Gabriel subsequently approved a $0.10 total lab spending ceiling.

## Step 2: Indexer (local checks and live build passed)

- `python3 indexer.py --dry-run`: 17 files, 78 chunks, 113,786 UTF-8 bytes after overlap. Conservative text-cost estimate at the recorded embedding price: $0.002276. No API calls.
- Manual Python assertions verified all chunk lengths are at most 250 words and adjacent chunks within each file share exactly 50 words.
- Cosine similarity: identical vectors score approximately 1; orthogonal vectors score 0.
- Empty, zero-norm, nonfinite, and boolean-containing vectors are rejected. Reordered embedding response indices are mapped correctly; duplicate indices are rejected.
- Temporary-file checks with simulated API and atomic-replacement failures preserved an existing index and left no temporary output. Missing corpus and missing credentials fail before embedding calls.
- A simulated complete build with two-dimensional fixture vectors wrote and reloaded an index containing 17 source hashes, 78 chunks, three batch usage entries, model identifier, chunk settings, build timestamp, and course revision. This checks the build path; fixture vectors are not real embeddings. Temporary output was deleted.
- The initial live attempt was blocked before any request because the credential source was not explicitly authorized. Gabriel then explicitly authorized the OpenRouter key in `keys.md` within the $0.10 budget. The subsequent live build succeeded. The key was passed through the process environment, not printed or committed.
- Live proof: 17 files, 78 chunks, three embedding requests, 1,536 dimensions per vector, and 25,944 input tokens. API-reported total cost: $0.00051888; remaining approved budget: $0.09948112. See `results/index-build.txt` and `results/budget.json`.
- Reloaded the actual JSON index and verified all source hashes against current files, all chunk text and offsets against source chunking, unique IDs, and every vector's dimension, finite values, and nonzero norm.
- The real index remains local and ignored by Git. No asker or evaluation results are claimed.
- Shared index loading and freshness checks were subsequently implemented and checked in step 3.
- Repository was published at https://github.com/Gabbykoms/cpsc415-week04 in step 1; remote main was verified at cb5adec. Later local commits are not yet pushed.

## Step 3: Asker (local checks and live proof passed)

- Implemented `asker.py` and shared index loading. Checks schema, model, dimensions, source hashes, chunk IDs/text/offsets, and vector validity before embedding calls.
- Local assertions verified descending top-five ranking, a real index vector retrieving its own chunk first, accepted source citations, rejected invented/missing citations, malformed and tampered index errors, source-hash changes, model mismatch, missing key, and blank question handling.
- A simulated baseline verified no index load and no question embedding; its prompt contains zero excerpts. A simulated invalid answer retained the raw answer and chat usage in its error record.
- Live supported question: “What percentage of the course grade is participation and labs?” Answer: 15%, citing `syllabus.md#chunk-7`. Checked the cited retrieved text: it explicitly assigns 15% to Participation and labs. Five chunks printed in descending score order. Cost: $0.00078772 including question embedding.
- Live unsupported question: “What is the instructor's favorite ice cream flavor?” Exact response: “I can't find that in the course documents.” Five retrieved chunks printed. Cost: $0.00056619 including question embedding.
- Live baseline: same grade-weight question and grounding instructions, without excerpts or embedding call. Exact required refusal. Cost: $0.00014237.
- Full raw answers, chunks, scores, model identifiers, prompts, index provenance, and API usage are in `results/asker-proof-*.json`; terminal captures are in matching `.txt` files.
- Total reported spend including the index: $0.00201516. Remaining approved budget: $0.09798484. No automatic retries performed.
- These three agent-selected proof checks are not the required five-question evaluation. They demonstrate these observed cases only; factual citation support still requires human review.

## Step 4: Five-question comparison complete

- Gabriel accepted the agent-suggested five questions unchanged. `questions.json` records provenance and expected answers/sources. Student-authorship requirement remains unmet. Questions and runner committed as `a21b50b` before paid evaluation.
- Local simulated-run checks verified ten captured outcomes, identical questions in both modes, continuation after a case error, refusal to overwrite prior results before API calls, and rejection of invalid question sets.
- Ran `python3 eval.py --output-dir cpsc415-week04/results/eval-01` via the project-relative executable from the parent workspace. It captured ten results and exited 1 due to one output-validation failure, not a network failure. Full terminal capture: `results/eval-terminal.txt`.
- Agent source review: **4/5 with retrieval; 1/5 without retrieval**. See `results/eval-01/review.json` for all judgments. Gabriel's independent review is pending; raw run records retain their original pending review marker.

| Case | With retrieval | Without retrieval |
|---|---|---|
| Week 4 deadline | FAIL: correct date, but extra citation points to a chunk not supplied. | FAIL: refuses an answerable question. |
| Portfolio grade weight | PASS: 25%, supported by syllabus chunk 7. | FAIL: refusal. |
| Week 3 submission tag | PASS: week03-submitted, supported by assignment chunk 1. Omitted repository-URL context, but the question asks for the tag. | FAIL: refusal. |
| One late day applied to Week 4 | PASS: October 20, 2026, 1:30 PM, supported by both syllabus policy and assignment deadline. | FAIL: refusal. |
| Favorite movie | PASS: exact refusal. | PASS: exact refusal. |

### Failure evidence
The with-retrieval deadline answer supplied the correct deadline but additionally cited `syllabus.md#chunk-1`, which was absent from the prompt. Retrieved chunks, in order: `assignments/week04-rag-plan.md#chunk-1`, `syllabus.md#chunk-14`, `weeks/03/README.md#chunk-2`, `assignments/week03-structured-output.md#chunk-1`, and `assignments/week05-vision-tests.md#chunk-1`. Correct deadline evidence was present; the failure was citation generation, not failure to retrieve the deadline. All texts and scores are preserved in `with_retrieval-deadline.json`.

The four baseline failures had no retrieved chunks by design. The grounding instruction required refusal with no supporting excerpts. The comparison demonstrates usefulness gained from excerpts under this prompt, not general model inability without retrieval. No prompt changes or reruns were made to conceal failures.

### Spending
Evaluation: 10 chat calls and 5 question-embedding calls; API-reported cost $0.00441969. Total lab spend so far: $0.00643485. Remaining approved budget: $0.09356515. Details in `results/budget.json`.

## Later steps
The stale-page experiment and Gabriel's code explanation remain pending. Do not create the submission tag yet.
