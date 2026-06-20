"""
BERT-based semantic embedding service.

Generates vector embeddings for CV text using a pre-trained
sentence-transformer model. These embeddings capture the MEANING
of text, not just keywords — so "built REST APIs using Python"
and "developed web services in Python" would have very similar
embeddings even though they share few words.

Used in Phase 4 to:
1. Compare job descriptions against CV experience semantically
2. Measure how relevant a candidate's experience is to a role
3. Go beyond simple keyword matching
"""
from sentence_transformers import SentenceTransformer

# Load model once at module level — first run downloads the model (~80MB)
# 'all-MiniLM-L6-v2' is fast, lightweight, and good for semantic similarity
_model = None


def _get_model():
    """Lazy-load the model on first use to speed up app startup."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text):
    """Generate a single embedding vector for a piece of text.

    Args:
        text: Any string (experience description, job description, etc.)

    Returns:
        List of floats — a 384-dimensional vector representing the text's meaning
    """
    if not text or len(text.strip()) < 5:
        return []

    model = _get_model()
    embedding = model.encode(text)
    return embedding.tolist()


def generate_embeddings_batch(texts):
    """Generate embeddings for multiple texts at once (faster than one by one).

    Args:
        texts: List of strings

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    model = _get_model()
    # Filter out empty texts but track their positions
    valid = [(i, t) for i, t in enumerate(texts) if t and len(t.strip()) >= 5]

    if not valid:
        return [[] for _ in texts]

    indices, valid_texts = zip(*valid)
    embeddings = model.encode(list(valid_texts))

    # Reconstruct the list with empty embeddings for filtered-out texts
    result = [[] for _ in texts]
    for idx, emb in zip(indices, embeddings):
        result[idx] = emb.tolist()

    return result


def compute_similarity(embedding1, embedding2):
    """Compute cosine similarity between two embeddings.

    Returns a float between -1 and 1, where:
      1.0  = identical meaning
      0.7+ = very similar
      0.5  = somewhat related
      0.0  = unrelated
    """
    if not embedding1 or not embedding2:
        return 0.0

    # Cosine similarity
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    norm1 = sum(a * a for a in embedding1) ** 0.5
    norm2 = sum(b * b for b in embedding2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)
