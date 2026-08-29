"""
Getting a document into the search index: extract → chunk → embed → store.
"""

from django.db import transaction

from ai.embeddings import embed_documents
from ai.models import DocumentChunk

# Characters, not words. Big enough to hold a whole clause of a policy,
# small enough that one chunk is about one idea.
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def extract_text(file_field):
    """Pull plain text out of an uploaded file."""
    name = file_field.name.lower()

    file_field.open("rb")
    try:
        if name.endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(file_field)
            # extract_text() returns None for image-only pages, so the `or ""`
            # matters — a scanned PDF gives you nothing, not a crash.
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)

        if name.endswith((".txt", ".md")):
            return file_field.read().decode("utf-8", errors="replace")
    finally:
        file_field.close()

    raise ValueError(f"Cannot read {name}. Supported: .pdf, .txt, .md")


def chunk_text(text):
    """
    Split text into overlapping pieces.

    Paragraphs are kept whole where possible: a sentence cut in half is half
    an idea, and half an idea embeds to the wrong place.

    The overlap is for the same reason. If the answer straddles a boundary,
    the repeated tail means at least one chunk holds all of it.
    """
    
    # Windows editors save "\r\n". Everything below splits on "\n\n", which
    # would never match — the whole file would look like one paragraph.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Hard-split anything bigger than a chunk first, so the packing loop
    # below only ever handles pieces that already fit.
    pieces = []
    for paragraph in paragraphs:
        while len(paragraph) > CHUNK_SIZE:
            pieces.append(paragraph[:CHUNK_SIZE])
            paragraph = paragraph[CHUNK_SIZE - CHUNK_OVERLAP :]
        if paragraph:
            pieces.append(paragraph)

    # Pack pieces together until adding one more would overflow.
    chunks = []
    current = ""
    for piece in pieces:
        if current and len(current) + len(piece) + 2 > CHUNK_SIZE:
            chunks.append(current)
            current = current[-CHUNK_OVERLAP:] + "\n\n" + piece
        else:
            current = f"{current}\n\n{piece}" if current else piece

    if current:
        chunks.append(current)

    return chunks


@transaction.atomic
def ingest(document):
    """
    Read a document, split it, embed it, store the chunks.

    Safe to run twice: old chunks are deleted first, so re-ingesting replaces
    instead of duplicating.
    """
    text = extract_text(document.file)
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError(f"No text found in {document.file.name}.")

    # Embed BEFORE deleting. If the API call fails, the document keeps the
    # chunks it already had rather than ending up empty and unsearchable.
    vectors = embed_documents(chunks)

    document.chunks.all().delete()

    DocumentChunk.objects.bulk_create(
        [
            DocumentChunk(
                document=document,
                # The ACL, copied down from the document. This is the column
                # the search filters on.
                employee=document.employee,
                chunk_index=index,
                content=content,
                embedding=vector,
            )
            for index, (content, vector) in enumerate(zip(chunks, vectors))
        ]
    )

    document.chunk_count = len(chunks)
    document.save(update_fields=["chunk_count", "updated_at"])

    return len(chunks)
