"""Smoke test cho ui_server: kiem tra SSE stream /api/chat voi fake provider.

Khong can API key, khong can mang that — dung fake provider trong tests.
Chay:
    python scripts/smoke_ui.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

import ui_server  # noqa: E402
from providers.base import ModelResponse, ToolCall  # noqa: E402


class FakeProvider:
    """Gọi `lookup` ở vòng 1, trả lời text ở vòng 2."""

    default_model = "fake-model"
    calls: list[dict] = []

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
        FakeProvider.calls.append({"n_messages": len(messages), "has_tools": bool(tools)})
        if len(FakeProvider.calls) == 1:
            return ModelResponse(
                text="",
                tool_calls=[ToolCall(name="lookup", args={"query": "AI", "topic": "news"})],
            )
        return ModelResponse(text="Day la cau tra loi tho cua agent.", tool_calls=[])


def main() -> int:
    ui_server.make_provider = lambda name: FakeProvider()

    client = TestClient(ui_server.app)
    failures: list[str] = []

    # --- GET /api/health ---
    health = client.get("/api/health")
    if health.status_code != 200 or health.json().get("status") != "ok":
        failures.append(f"health: {health.status_code} {health.text}")
    print("health           :", health.status_code, health.json())

    # --- GET /api/tools ---
    tools_resp = client.get("/api/tools")
    tools_body = tools_resp.json()
    names = [t["name"] for t in tools_body.get("tools", [])]
    print("tools            :", tools_resp.status_code, names)
    if "lookup" not in names:
        failures.append("tools: khong thay 'lookup'")
    if "wikipedia" not in tools_body.get("implemented", []):
        print("  (wikipedia chua duoc implement - dung roi role C)")

    # --- GET / ---
    index = client.get("/")
    print("index            :", index.status_code, f"{len(index.content)} bytes")
    if index.status_code != 200 or "__OpenUI" not in index.text:
        failures.append("index: khong tim thay __OpenUI trong HTML")

    # --- POST /api/chat (SSE) ---
    with client.stream(
        "POST",
        "/api/chat",
        json={"message": "Tin AI hôm nay co gi?", "provider": "openrouter", "version": "v3"},
    ) as resp:
        events: list[tuple[str, dict]] = []
        event_name = ""
        for line in resp.iter_lines():
            if line.startswith("event: "):
                event_name = line[7:].strip()
            elif line.startswith("data: "):
                events.append((event_name, json.loads(line[6:])))

    print("sse events       :", [e for e, _ in events])
    event_names = [e for e, _ in events]
    for required in ("start", "tool_call", "tool_result", "answer", "done"):
        if required not in event_names:
            failures.append(f"sse: thieu event '{required}'")

    tool_call = next((d for e, d in events if e == "tool_call"), None)
    if tool_call is None or tool_call.get("name") != "lookup":
        failures.append(f"sse: tool_call sai -> {tool_call}")
    else:
        print("tool_call args   :", tool_call.get("args"))

    done = next((d for e, d in events if e == "done"), None)
    print("done status      :", (done or {}).get("status"))

    # Pha 1 phai dung dung system_prompt.md cua starter (khong bi OpenUI prompt loa).
    first_call = FakeProvider.calls[0]
    print("phase1 has_tools :", first_call["has_tools"], "(True = agent goi tool that)")

    print()
    if failures:
        print("FAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("PASS: ui_server smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
