"""Shared file, vector, and API helpers for the course RAG lab."""
import hashlib
import json
import math
import os
from pathlib import Path
import urllib.error
import urllib.request

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_COURSE_DIR = PROJECT_DIR.parent / 'ai-integration-course'
DEFAULT_INDEX = PROJECT_DIR / 'index.json'


class RagError(Exception):
    """An actionable error safe to show at the terminal."""


def discover_sources(course_dir):
    root = Path(course_dir).resolve()
    locations = [root / 'syllabus.md', root / 'assignments']
    locations += [root / 'weeks' / week for week in ('01', '02', '03')]
    sources = []
    for location in locations:
        if location.is_symlink() or any(p.is_symlink() for p in location.parents if p != root):
            raise RagError('Corpus locations must not use symlinks.')
        if location.name == 'syllabus.md':
            if not location.is_file():
                raise RagError('Missing syllabus.md; check --course-dir.')
            candidates = [location]
        else:
            if not location.is_dir():
                raise RagError(f'Missing required directory: {location.relative_to(root)}.')
            candidates = sorted(location.rglob('*.md'))
        accepted = []
        for path in candidates:
            if path.is_symlink():
                continue
            # Never follow a directory symlink, even to another allowed page.
            if any(parent.is_symlink() for parent in path.parents if parent != root):
                continue
            if not path.is_file() or not path.resolve().is_relative_to(root):
                continue
            raw = path.read_bytes()
            try:
                content = raw.decode('utf-8')
            except UnicodeDecodeError as exc:
                raise RagError(f'Non-UTF-8 Markdown: {path.relative_to(root)}') from exc
            accepted.append({'source': path.relative_to(root).as_posix(),
                             'text': content, 'sha256': hashlib.sha256(raw).hexdigest()})
        if not accepted or not any(item['text'].strip() for item in accepted):
            raise RagError(f'No nonempty Markdown in {location.relative_to(root)}.')
        sources.extend(accepted)
    return sorted(sources, key=lambda item: item['source'])


def make_chunks(sources, size=250, overlap=50):
    if not 0 <= overlap < size:
        raise RagError('Chunk overlap must be nonnegative and smaller than size.')
    chunks = []
    for source in sources:
        words = source['text'].split()
        for start in range(0, len(words), size - overlap):
            end = min(start + size, len(words))
            chunks.append({'id': f"{source['source']}#chunk-{start // (size - overlap) + 1}",
                           'source': source['source'], 'word_start': start, 'word_end': end,
                           'text': ' '.join(words[start:end])})
            if end == len(words):
                break
    if not chunks:
        raise RagError('The corpus produced no chunks.')
    return chunks


def validate_vector(vector, dimension=None):
    if not isinstance(vector, list) or not vector:
        raise RagError('Embedding must be a nonempty list.')
    if dimension is not None and len(vector) != dimension:
        raise RagError('Embedding dimensions do not match.')
    if any(type(value) not in (int, float) or not math.isfinite(value) for value in vector):
        raise RagError('Embedding contains invalid or nonfinite numbers.')
    norm = math.hypot(*vector)
    if not math.isfinite(norm) or norm == 0:
        raise RagError('Embedding has invalid or zero norm.')
    return norm


def cosine_similarity(left, right):
    left_norm = validate_vector(left)
    right_norm = validate_vector(right, len(left))
    return sum((a / left_norm) * (b / right_norm) for a, b in zip(left, right))


def api_key():
    key = os.getenv('OPENROUTER_API_KEY', '').strip()
    if not key:
        raise RagError('Set OPENROUTER_API_KEY before making API calls.')
    return key


def post_json(endpoint, payload):
    key = api_key()
    base = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1').rstrip('/')
    if not base.startswith('https://'):
        raise RagError('OPENROUTER_BASE_URL must use HTTPS.')
    request = urllib.request.Request(base + endpoint,
        data=json.dumps(payload, allow_nan=False).encode(),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        method='POST')
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RagError(f'API HTTP {exc.code}; no automatic retry was made.') from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RagError('API connection failed or timed out; no automatic retry was made.') from exc
    except (ValueError, UnicodeDecodeError) as exc:
        raise RagError('API returned invalid JSON.') from exc
    if not isinstance(result, dict) or 'error' in result:
        raise RagError('API returned an error or unexpected response shape.')
    return result


def embed_texts(texts, model):
    response = post_json('/embeddings', {'model': model, 'input': texts, 'encoding_format': 'float'})
    rows = response.get('data')
    if not isinstance(rows, list) or len(rows) != len(texts):
        raise RagError('API returned an incomplete embedding batch.')
    ordered = [None] * len(texts)
    dimension = None
    for row in rows:
        if not isinstance(row, dict):
            raise RagError('Invalid embedding entry.')
        index = row.get('index')
        if type(index) is not int or not 0 <= index < len(texts) or ordered[index] is not None:
            raise RagError('Invalid or duplicate embedding response index.')
        vector = row.get('embedding')
        validate_vector(vector, dimension)
        dimension = len(vector)
        ordered[index] = vector
    return ordered, response.get('usage')
