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

## Step 2: Indexer (local checks passed; live build pending)

- `python3 indexer.py --dry-run`: 17 files, 78 chunks, 113,786 UTF-8 bytes after overlap. Conservative text-cost estimate at the recorded embedding price: $0.002276. No API calls.
- Manual Python assertions verified all chunk lengths are at most 250 words and adjacent chunks within each file share exactly 50 words.
- Cosine similarity: identical vectors score approximately 1; orthogonal vectors score 0.
- Empty, zero-norm, nonfinite, and boolean-containing vectors are rejected. Reordered embedding response indices are mapped correctly; duplicate indices are rejected.
- Temporary-file checks with simulated API and atomic-replacement failures preserved an existing index and left no temporary output. Missing corpus and missing credentials fail before embedding calls.
- A simulated complete build with two-dimensional fixture vectors wrote and reloaded an index containing 17 source hashes, 78 chunks, three batch usage entries, model identifier, chunk settings, build timestamp, and course revision. This checks the build path; fixture vectors are not real embeddings. Temporary output was deleted.
- Live execution was blocked before the request: automatic approval review rejected extracting a credential from `keys.md` without explicit authorization of that credential source. No paid request ran; no real index exists yet.
- Shared index loading and freshness checks will be implemented with the asker in step 3.
- Repository was published at https://github.com/Gabbykoms/cpsc415-week04 in step 1; remote main was verified at cb5adec. Later local commits are not yet pushed.

## Later steps
Asker, evaluation, stale-page findings, and code explanation are pending. No live retrieval or evaluation results are claimed.
