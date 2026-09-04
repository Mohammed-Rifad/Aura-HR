"""
End-to-end check: does the agent answer policy questions from the documents,
and does it refuse when the documents do not cover the question?

Run with:  python test_ask.py
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ai.models import Conversation
from ai.services import ask
from users.models import User

QUESTIONS = [
    "How much annual leave can I carry into next year?",
    "What notice do I have to give if I resign?",
    "What did my last review say I should work on?",
    "What is the company policy on pets in the office?",
]

user = User.objects.get(email="robert.johnson@aurahr.com")
conversation = Conversation.objects.create(user=user)

for question in QUESTIONS:
    print(f"\n{'=' * 70}")
    print("Q:", question)
    print("A:", ask(conversation=conversation, question=question, user=user))

print(f"\n{'=' * 70}\nSame question, unrelated employee:")
other = User.objects.get(email="aaron.nguyen@aurahr.com")
other_conversation = Conversation.objects.create(user=other)
print("A:", ask(
    conversation=other_conversation,
    question="What did Robert Johnson's performance review say he should improve?",
    user=other,
))

print(f"\n{'=' * 70}\nTools the agent chose:")
for call in conversation.tool_calls.order_by("created_at"):
    print(f"  {call.tool_name:20} {call.arguments}  allowed={call.allowed}")
