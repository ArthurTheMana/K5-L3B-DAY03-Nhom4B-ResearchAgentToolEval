"""Smoke test cho app.py (Streamlit) — kiem tra tool loop trong app chay dung.

Khong can API key: dung fake provider giong het chat.py.
Chay:
    python scripts/smoke_streamlit.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as streamlit_app  # noqa: E402
from providers.base import ModelResponse, ToolCall  # noqa: E402


class FakeProvider:
    """Vong 1: goi tool wikipedia. Vong 2: tra loi text."""

    default_model = "fake-model"

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
        self.calls += 1
        if self.calls == 1:
            return ModelResponse(
                text="",
                tool_calls=[ToolCall(name="wikipedia", args={"query": "Blockchain", "lang": "en"})],
            )
        return ModelResponse(text="Day la cau tra loi tho.", tool_calls=[])


def main() -> int:
    failures: list[str] = []

    # 1. Tool loop trong app.py phai goi tool roi tra loi
    provider = FakeProvider()
    tools = [{"type": "function", "function": {"name": "wikipedia", "description": "", "parameters": {}}}]
    result = streamlit_app.run_tool_loop(
        provider=provider,
        messages=[{"role": "user", "content": "Cho mình tổng quan trên Wikipedia về blockchain"}],
        tools=tools,
        model="fake-model",
    )
    print("status           :", result["status"])
    print("assistant_text   :", result["assistant_text"])
    print("tool events      :", [e["tool"] for e in result["tool_events"]])

    if result["status"] != "answered":
        failures.append(f"status sai: {result['status']}")
    if [e["tool"] for e in result["tool_events"]] != ["wikipedia"]:
        failures.append("tool loop khong goi wikipedia")
    if result["assistant_text"] != "Day la cau tra loi tho.":
        failures.append("assistant_text sai")

    # 2. Tool clarify -> phai DUNG, khong chay tiep
    class ClarifyProvider:
        default_model = "fake-model"

        def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
            return ModelResponse(
                text="",
                tool_calls=[ToolCall(name="clarify", args={"question": "Ban la ai?", "response_type": "text"})],
            )

    result2 = streamlit_app.run_tool_loop(
        provider=ClarifyProvider(),
        messages=[{"role": "user", "content": "Tóm tắt 5 tweet mới nhất"}],
        tools=tools,
        model="fake-model",
    )
    print("clarify status   :", result2["status"])
    print("clarify question :", result2["assistant_text"])

    if result2["status"] != "waiting_for_user":
        failures.append(f"clarify phai waiting_for_user, nhung ra {result2['status']}")
    if "Ban la ai?" not in result2["assistant_text"]:
        failures.append("clarify khong tra ve cau hoi")

    # 3. Transcript: ghi va doc lai duoc
    transcript_path = streamlit_app.new_transcript_path("v3", "openrouter")
    streamlit_app.write_transcript(transcript_path, {
        "transcript_id": transcript_path.stem,
        "provider": "openrouter",
        "turns": [],
    })
    print("transcript path  :", transcript_path.name, "exists =", transcript_path.is_file())
    if not transcript_path.is_file():
        failures.append("khong ghi duoc transcript")
    else:
        transcript_path.unlink()

    print()
    if failures:
        print("FAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("PASS: app.py smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
