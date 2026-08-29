"""
Searching the knowledge base by meaning.

The permission check lives inside the query on purpose. See search_chunks.
"""

from django.db.models import Q
from pgvector.django import CosineDistance

from ai.embeddings import embed_query
from ai.models import DocumentChunk
from common.scoping import visible_employee_filter, visible_employees

# How many chunks to hand the model. More is not better — every irrelevant
# chunk is another chance for it to answer from the wrong one.
TOP_K = 5

# Cosine distance runs from 0 (same meaning) to 2 (opposite). Past this, a
# chunk is not really about the question. Without a floor, a question with no
# answer in the documents still returns the five least-bad chunks, and the
# model answers confidently from them.
MAX_DISTANCE = 0.75


def search_chunks(*, query, user, limit=TOP_K):
    """The chunks most related to `query` that `user` is allowed to read."""
    vector = embed_query(query)

    # ---- the security line -------------------------------------------------
    #
    # A chunk is readable if it belongs to no employee (company-wide) or to an
    # employee this user can already see.
    #
    # This is part of the SQL, so the database never even ranks rows the user
    # cannot read. Filtering afterwards in Python would be a real bug: the
    # nearest five rows would be picked from EVERYONE's documents and then
    # thinned, so a user could get two results, or none, because someone
    # else's private document outranked their own. The permission check has
    # to happen before the ordering, not after.
    scope = visible_employee_filter(user)
    if scope is None:
        # Admin and HR — no restriction at all. Skipping the subquery here
        # keeps the plan simple for the common case.
        permitted = Q()
    else:
        permitted = Q(employee__isnull=True) | Q(
            employee__in=visible_employees(user)
        )
    # -----------------------------------------------------------------------

    return list(
        DocumentChunk.objects.filter(permitted, document__is_active=True)
        .annotate(distance=CosineDistance("embedding", vector))
        .filter(distance__lt=MAX_DISTANCE)
        .order_by("distance")
        .select_related("document")[:limit]
    )
