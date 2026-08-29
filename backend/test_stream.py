"""
Watch the stream arrive.

The point is the TIMING column — events should appear seconds apart. If they
all land at once, nothing is actually streaming.

Start the server first, then:  python test_stream.py
"""

import time

import httpx

BASE = "http://localhost:8000/api/v1"
EMAIL = "manager@aurahr.com"
PASSWORD = "Password@123"

login = httpx.post(f"{BASE}/auth/login/", json={"email": EMAIL, "password": PASSWORD})
login.raise_for_status()
access = login.json()["access"]

started = time.monotonic()

with httpx.stream(
    "POST",
    f"{BASE}/ai/chat/stream/",
    headers={"Authorization": f"Bearer {access}"},
    json={"message": "How many people work in Engineering?"},
    timeout=120,
) as response:
    print("status:", response.status_code)
    print("content-type:", response.headers.get("content-type"))
    print()

    for line in response.iter_lines():
        if line.startswith("data: "):
            print(f"{time.monotonic() - started:6.1f}s  {line[6:]}")
