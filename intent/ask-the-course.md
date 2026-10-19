# Intent: Ask the course

## Goal
Build a terminal program that serves as a general reference for CPSC 415. Answer questions using only the assigned course Markdown pages, cite supporting pages, and print retrieved passages with their similarity scores.

## Who it is for
Gabriel Koomson, who wants to look up course information without manually searching multiple pages.

## Constraints
- Read syllabus.md, assignments/, and weeks/01 through weeks/03 directly from ../ai-integration-course. Skip weeks/04; never copy course pages into this repository.
- If the documents do not contain the answer, reply: "I can't find that in the course documents."
- Keep API keys out of the repository.
- Review and approve the specification and implementation plan before writing code.
- Submit the repository URL and week04-submitted tag on Moodle. Deadline: October 19, 2026, at 1:30 PM.

## Not in scope
A web interface, outside information, or a general-purpose assistant unrelated to the course.

## Success looks like
1. A terminal question receives a useful answer with source citations and retrieved passages with scores.
2. Questions unsupported by the documents receive the required refusal.
3. Five student-written questions are evaluated with and without retrieval, and the observed difference and stale-page behavior are documented honestly.

## Open questions
None about the intended use. Language, models, chunking, and error handling will be proposed in the specification for review.

**Approved by:** Gabriel Koomson, October 19, 2026, in conversation.
