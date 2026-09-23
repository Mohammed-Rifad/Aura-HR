"""
Runs one case and writes down what happened.

No scoring here. This file answers "what did the agent do?", and the
scorers in metrics.py decide whether that was right.
"""

from dataclasses import dataclass, field

from django.contrib.auth import get_user_model

from ai.evals.case import EvalCase
from ai.models import Conversation
from ai.services import ask

User = get_user_model()

# Keys a tool uses for "here is what I found". Present and empty means it
# found nothing. Same list as services._found_nothing.
RESULT_KEYS = ("employees", "documents", "requests", "passages")


@dataclass
class CaseRun:
    """What actually happened when one case was asked."""

    case: EvalCase

    # Tools the model asked for. Includes ones the gate refused to run.
    requested: list[str] = field(default_factory=list)

    # Tools that actually executed. The gate's whole purpose is to make
    # this list shorter than the one above.
    executed: list[str] = field(default_factory=list)

    # Tools that ran and came back with nothing.
    empty: list[str] = field(default_factory=list)

    # Did the agent create a PendingAction — a write awaiting a human?
    proposed: bool = False

    # Document titles that retrieval surfaced.
    retrieved: list[str] = field(default_factory=list)

    answer: str = ""

    # Set when the run itself blew up — a provider outage, a rate limit.
    # Not the same as the agent refusing, which is a valid outcome.
    error: str = ""


def _tool_responses(conversation):
    """
    Every tool result the model was handed, in order.

    Read back out of the saved conversation rather than captured live, so
    the runner needs no hooks inside the agent loop.
    """
    results = []
    for message in conversation.messages.all():
        for part in message.parts:
            response = part.get("function_response")
            if response:
                results.append((response["name"], response.get("response") or {}))
    return results


def _found_nothing(result):
    """Did this tool come back empty?"""
    if not isinstance(result, dict) or "error" in result:
        return False
    return any(key in result and not result[key] for key in RESULT_KEYS)


def _documents(result):
    """Document titles inside a search_policies result."""
    passages = result.get("passages") or []
    return [p["source"] for p in passages if isinstance(p, dict) and "source" in p]


def run_case(case: EvalCase) -> CaseRun:
    """Ask one question as one person, and record what happened."""
    user = User.objects.get(email=case.asked_by)
    conversation = Conversation.objects.create(user=user)

    run = CaseRun(case=case)

     # Two attempts. A dropped connection or a rate limit is not the agent
    # being wrong, and letting it count as a failure means your scores
    # measure your internet as much as your prompt.
    last_error = ""
    for attempt in range(2):
        try:
            run.answer = ask(
                conversation=conversation,
                question=case.question,
                user=user,
            )
            last_error = ""
            break
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt == 0:
                # Fresh conversation — the failed one has a half-written
                # turn in it that would confuse the retry.
                conversation = Conversation.objects.create(user=user)
                run = CaseRun(case=case)

    if last_error:
        run.error = last_error
        return run

    for name, result in _tool_responses(conversation):
        run.requested.append(name)

        if _found_nothing(result) or result.get("error"):
            run.empty.append(name)

        run.retrieved.extend(_documents(result))

    # AIToolCall rows are written by run_tool, and only by run_tool. So this
    # is the list of tools that genuinely executed — the gate's refusals
    # never appear here.
    run.executed = list(
        conversation.tool_calls.order_by("created_at").values_list(
            "tool_name", flat=True
        )
    )

    run.proposed = conversation.pending_actions.exists()

    return run
