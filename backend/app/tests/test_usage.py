import os
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import json
import respx
from fastapi.testclient import TestClient
from httpx import Response

from app.main import app, OPENAI_API_BASE

client = TestClient(app)

@respx.mock
def test_chat_and_summary():
    # Mock OpenAI Chat Completions
    respx.post(f"{OPENAI_API_BASE}/chat/completions").mock(
        return_value=Response(
            200,
            json={
                "id": "chatcmpl_123",
                "choices": [
                    {"index": 0, "message": {"role": "assistant", "content": "Hello!"}},
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
            },
        )
    )

    payload = {
        "api_key": "sk-test",
        "model": "gpt-5-mini",
        "user_label": "alice",
        "prompt": "Say hello",
    }

    r = client.post("/api/llm/chat", json=payload)
    assert r.status_code == 200
    assert r.json()["content"] == "Hello!"

    r2 = client.get("/api/usage/summary")
    assert r2.status_code == 200
    data = r2.json()

    assert len(data) == 1
    row = data[0]
    assert row["model"] == "gpt-5-mini"
    assert row["user_label"] == "alice"
    assert row["total_input_tokens"] == 5
    assert row["total_output_tokens"] == 3