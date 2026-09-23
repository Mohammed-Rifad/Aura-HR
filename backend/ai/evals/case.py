"""
One evaluation case.

Deliberately not about the words the model produces — those change every
run. Every field here is something that either happened or did not.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvalCase:
    """A question, who asks it, and what should happen."""

    id: str
    question: str

    # Which account asks. The same question from two people should often
    # produce two different outcomes — that is the point of most of these.
    asked_by: str

    # Tools that MUST be called for this to pass.
    must_call: list[str] = field(default_factory=list)

    # Tools that must NOT be called. The important half of the suite:
    # proving something did not happen.
    must_not_call: list[str] = field(default_factory=list)

    # True when the agent should come back empty-handed — either because
    # the data is out of scope, or because it does not exist.
    should_refuse: bool = False

    # True when the agent should create a PendingAction — a write it wants
    # a human to confirm. False means no proposal may exist afterwards,
    # which is how the gate cases prove a refusal.
    should_propose: bool = False

    # The title of the document retrieval should surface, if this is a
    # policy question.
    should_retrieve: str | None = None

    # Why this case exists. Read by a person, not the runner.
    note: str = ""
