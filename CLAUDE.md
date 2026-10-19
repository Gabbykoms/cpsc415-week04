# Project conventions

## What this repository is
Week 4 terminal course-reference RAG lab. See [intent](intent/ask-the-course.md) and [specification](spec.md).

## Commands
Not implemented yet. Proposed commands are in spec.md.

## Conventions
- Keep approval and evaluation records honest. Never mark a draft approved without Gabriel's approval.
- Student writes the five evaluation questions and asks at least two questions about the plan.

## Working rules
- This is the Week 4 introductory lab. Stages assigned: intent, spec, and plan. No branches or pull requests yet. Commit to main.
- Libraries and build tools are allowed. Name each dependency in spec.md with its reason. Print retrieved chunks and scores for every answer.
- Documents are in ../ai-integration-course: syllabus.md, assignments/, and weeks/01 through weeks/03. Skip weeks/04. Never copy pages into this repo.
- Intent is approved. Get the spec reviewed and approved, then the plan questioned and approved, before any code is written.
- During implementation, stop after each plan step and show its proof before starting the next.
- Never commit API keys, .env, or .claude/settings.local.json.

## Common mistakes
- Do not treat similarity scores as probabilities or evidence of factual correctness.
- Do not claim evaluation results or student corrections that have not occurred.
