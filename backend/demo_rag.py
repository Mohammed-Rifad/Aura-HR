"""
End-to-end check: does the agent answer policy questions from the documents,
and does it refuse when the documents do not cover the question?

Run with:  python test_ask.py
"""

import os
from ai.search import search_chunks
from users.models import User
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()



QUESTIONS = [
    "how many days of annual leave do I get",
    "what did Robert Johnson need to improve",
]

PEOPLE = [
    ("robert.johnson@aurahr.com", "the subject of the review"),
    ("manager@aurahr.com", "his manager"),
    ("aaron.nguyen@aurahr.com", "an unrelated employee"),
    ("admin@aurahr.com", "an admin"),
]

for question in QUESTIONS:
    print(f"\n{'=' * 70}\nQ: {question}\n{'=' * 70}")

    for email, description in PEOPLE:
        user = User.objects.get(email=email)
        results = search_chunks(query=question, user=user)

        print(f"\n  {description} ({user.role})")
        if not results:
            print("    nothing found")
        for chunk in results:
            print(f"    {chunk.distance:.3f}  {chunk.document.title}  #{chunk.chunk_index}")
