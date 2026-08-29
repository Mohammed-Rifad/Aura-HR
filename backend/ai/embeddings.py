"""
Turning text into vectors.

An embedding is a list of numbers describing what a piece of text MEANS.
Two texts about the same thing land close together even when they share no
words — "how much holiday do I get" and "annual leave entitlement is 30
days" have almost nothing in common as letters, but nearly the same meaning.
That closeness is what makes search-by-meaning possible.
"""

from django.conf import settings
from google.genai import types

from ai.client import get_client

# One API call per chunk would be slow and wasteful. This many go up together.
BATCH_SIZE = 50


def _embed(texts, *, task_type):
    if not texts:
        return []

    vectors = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]

        # Each text MUST be its own Content object. Hand the SDK a plain list
        # of strings and it merges them into one document — you get back a
        # single vector instead of len(batch), with no error to tell you.
        contents = [
            types.Content(role="user", parts=[types.Part(text=text)])
            for text in batch
        ]

        response = get_client().models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=contents,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=settings.EMBEDDING_DIM,
            ),
        )
        vectors.extend(item.values for item in response.embeddings)

    return vectors


def embed_documents(texts):
    """Vectors for text being STORED."""
    return _embed(texts, task_type="RETRIEVAL_DOCUMENT")


def embed_query(text):
    """Vector for a question being ASKED."""
    return _embed([text], task_type="RETRIEVAL_QUERY")[0]
