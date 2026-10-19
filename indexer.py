"""Build a local JSON embedding index of the permitted course pages."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from rag_common import (DEFAULT_COURSE_DIR, DEFAULT_INDEX, RagError, api_key,
                        discover_sources, embed_texts, make_chunks, validate_vector)


def course_revision(root):
    try:
        return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def save_index(path, index):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name + '.', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(index, stream, allow_nan=False)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_index(course_dir, output, dry_run=False):
    root = Path(course_dir).resolve()
    output = Path(output).resolve()
    if output.is_relative_to(root):
        raise RagError('Save the index outside the course repository.')
    if not output.parent.is_dir() or output.is_dir():
        raise RagError('Index output must be a file in an existing directory.')
    sources = discover_sources(root)
    chunks = make_chunks(sources)
    model = os.getenv('EMBEDDING_MODEL', 'openai/text-embedding-3-small').strip()
    if not model:
        raise RagError('EMBEDDING_MODEL must not be empty.')
    print(f'Corpus: {len(sources)} files, {len(chunks)} chunks (250 words, 50 overlap).', flush=True)
    # UTF-8 bytes conservatively overestimate ordinary text token counts.
    byte_count = sum(len(chunk['text'].encode('utf-8')) for chunk in chunks)
    if model == 'openai/text-embedding-3-small':
        print(f'Embedding input: {byte_count} UTF-8 bytes; estimated text cost upper bound '
              f'${byte_count * 0.02 / 1_000_000:.6f} at the recorded price (not a provider cap).', flush=True)
    if dry_run:
        print('Dry run: no API calls; no index written.')
        return None
    api_key()
    batches = []
    dimension = None
    for start in range(0, len(chunks), 32):
        batch = chunks[start:start + 32]
        vectors, usage = embed_texts([chunk['text'] for chunk in batch], model)
        # Show returned usage immediately, even if a later batch fails.
        print(f'Batch {start // 32 + 1}: {len(batch)} vectors; usage: '
              f'{json.dumps(usage) if usage is not None else "unavailable"}', flush=True)
        batches.append(usage)
        for chunk, vector in zip(batch, vectors):
            validate_vector(vector, dimension)
            dimension = len(vector)
            chunk['vector'] = vector
    hashes = {source['source']: source['sha256'] for source in sources}
    if hashes != {s['source']: s['sha256'] for s in discover_sources(root)}:
        raise RagError('Course files changed during indexing; existing index preserved. Rebuild.')
    index = {'schema_version': 1, 'embedding_model': model, 'dimension': dimension,
             'chunk_size_words': 250, 'overlap_words': 50,
             'source_hashes': hashes, 'course_git_revision': course_revision(root),
             'built_at': datetime.now(timezone.utc).isoformat(),
             'embedding_usage': batches, 'chunks': chunks}
    save_index(output, index)
    print(f'Saved {len(chunks)} chunks with {dimension}-dimensional vectors to {output.name}.')
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-dir', type=Path, default=DEFAULT_COURSE_DIR)
    parser.add_argument('--output', type=Path, default=DEFAULT_INDEX)
    parser.add_argument('--dry-run', action='store_true', help='Inspect the corpus without API calls.')
    args = parser.parse_args()
    try:
        build_index(args.course_dir, args.output, args.dry_run)
        return 0
    except (RagError, OSError) as exc:
        message = str(exc) if isinstance(exc, RagError) else 'File operation failed; check paths and permissions.'
        print(f'Error: {message}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
