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
- No paid API calls made. Spending ceiling pending Gabriel's confirmation.

## Later steps
Indexer, asker, evaluation, stale-page findings, and code explanation are pending. No pass counts or results are claimed.
