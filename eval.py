"""Capture the same five questions with and without retrieval for review."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from asker import ask
from rag_common import (PROJECT_DIR, DEFAULT_COURSE_DIR, DEFAULT_INDEX, RagError,
                        api_key, load_index)


def read_questions(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise RagError('Cannot read questions JSON.') from exc
    if not isinstance(data, dict) or not isinstance(data.get('provenance'), str):
        raise RagError('Questions must include a provenance statement.')
    questions = data.get('questions')
    if not isinstance(questions, list) or len(questions) != 5:
        raise RagError('Exactly five questions are required.')
    ids = set()
    kinds = []
    for question in questions:
        if not isinstance(question, dict):
            raise RagError('Each question must be an object.')
        for field in ('id', 'kind', 'question', 'expected_answer', 'purpose'):
            if not isinstance(question.get(field), str) or not question[field].strip():
                raise RagError(f'Question requires nonempty {field}.')
        identifier = question['id']
        if not all(c in 'abcdefghijklmnopqrstuvwxyz0123456789_' for c in identifier) or identifier in ids:
            raise RagError('Question IDs must be unique lowercase letters, digits, or underscores.')
        ids.add(identifier)
        kinds.append(question['kind'])
        sources = question.get('expected_sources')
        if not isinstance(sources, list) or any(not isinstance(s, str) or not s.strip() for s in sources):
            raise RagError('Expected sources must be a list of nonempty paths.')
        count = len(set(sources))
        if ((question['kind'] == 'single_source' and count != 1)
                or (question['kind'] == 'multi_source' and count < 2)
                or (question['kind'] == 'unanswerable' and count != 0)):
            raise RagError('Expected sources do not match question kind.')
    if sorted(kinds) != sorted(['single_source'] * 3 + ['multi_source', 'unanswerable']):
        raise RagError('Require three single-source, one multi-source, and one unanswerable question.')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--questions', type=Path, default=PROJECT_DIR / 'questions.json')
    parser.add_argument('--index', type=Path, default=DEFAULT_INDEX)
    parser.add_argument('--course-dir', type=Path, default=DEFAULT_COURSE_DIR)
    parser.add_argument('--output-dir', type=Path, help='New directory; existing results are never overwritten.')
    args = parser.parse_args()
    output = args.output_dir or PROJECT_DIR / 'results' / datetime.now(timezone.utc).strftime('eval-%Y%m%dT%H%M%S%fZ')
    try:
        data = read_questions(args.questions)
        index = load_index(args.index, args.course_dir,
                           os.getenv('EMBEDDING_MODEL', 'openai/text-embedding-3-small').strip())
        for question in data['questions']:
            if not set(question['expected_sources']) <= set(index['source_hashes']):
                raise RagError('An expected source is outside the indexed corpus.')
        api_key()
        if not os.getenv('CHAT_MODEL', 'minimax/minimax-m3').strip():
            raise RagError('CHAT_MODEL must not be empty.')
        output.mkdir(parents=True, exist_ok=False)
        (output / 'questions.json').write_text(json.dumps(data, indent=2) + '\n')
        outcomes = []
        for mode in ('with_retrieval', 'without_retrieval'):
            for question in data['questions']:
                print(f"\n=== {mode}: {question['id']} ===", flush=True)
                record = ask(question['question'], args.index, args.course_dir,
                             no_retrieval=mode == 'without_retrieval')
                record['evaluation_case'] = question
                record['review'] = {'verdict': 'pending', 'reason': 'Review against expected answer and cited evidence.'}
                filename = f"{mode}-{question['id']}.json"
                (output / filename).write_text(json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
                outcomes.append({'mode': mode, 'id': question['id'], 'status': record['status'],
                                 'record': filename, 'usage': record['usage']})
                (output / 'summary.json').write_text(json.dumps(
                    {'provenance': data['provenance'], 'outcomes': outcomes,
                     'semantic_review': 'pending; API/output success is not an evaluation pass'}, indent=2) + '\n')
        failures = sum(item['status'] != 'ok' for item in outcomes)
        print(f'Captured {len(outcomes)} outcomes; {failures} API/output errors. Semantic grading pending. Results: {output}')
        return 1 if failures else 0
    except (RagError, OSError) as exc:
        message = str(exc) if isinstance(exc, RagError) else 'File operation failed; use a new writable results directory.'
        print(f'Error: {message}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
