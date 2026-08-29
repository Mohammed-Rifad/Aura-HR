"""
The one place that talks to the AI provider.

Everything else in this app calls complete(). If we ever switch provider or
model, it changes here and nowhere else.
"""

from django.conf import settings
from google import genai
from google.genai import types

_client = None

# How long the AI's answer may be, in tokens (roughly 3/4 of a word each).
MAX_OUTPUT_TOKENS = 8192


def get_client():
    """
    Build the connection once and reuse it.

    A new client per request would open a fresh connection pool each time.
    """
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env."
            )
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def complete(*, system, contents, tools=None):
    """
    One turn of a conversation.

    system   — standing instructions, the same every turn
    contents — the conversation so far
    tools    — the functions the model is allowed to ask for

    Returns the raw response so the caller can see what the model decided.
    This module knows HOW to call the AI. The agent service decides WHAT to
    say and WHICH tools to actually run.
    """
    config = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        # Turned OFF deliberately. Left on, the SDK executes tool functions
        # by itself — no permission check, and no moment in between where a
        # human could approve a write. Our loop runs the tools, so our rules
        # always apply.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    if tools:
        # Gemini wants the function list wrapped in a Tool object.
        config.tools = [types.Tool(function_declarations=tools)]

    return get_client().models.generate_content(
        model=settings.AI_MODEL,
        contents=contents,
        config=config,
    )
