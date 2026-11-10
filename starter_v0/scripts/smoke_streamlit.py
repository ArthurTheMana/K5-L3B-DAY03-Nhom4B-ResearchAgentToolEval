"""Smoke test cho app.py (Streamlit) — kiểm tra tool loop + streaming trong app.

Không cần API key: dùng fake provider giống hệt chat.py.
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

TOOLS = [{"type": "function", "function": {"name": "wikipedia", "description": "", "parameters": {}}}]


class WikiThenAnswer:
    """Vòng 1: gọi tool wikipedia. Vòng 2: trả lời text."""

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


class ClarifyProvider:
    """Luôn hỏi lại bằng tool clarify."""

    default_model = "fake-model"

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
        return ModelResponse(
            text="",
            tool_calls=[ToolCall(name="clarify", args={"question": "Ban la ai?", "response_type": "text"})],
        )


def drain(gen):
    """Lấy hết event từ generator, giữ lại thứ tự (thứ tự là thứ tự stream)."""
    return list(gen)


def main() -> int:
    failures: list[str] = []

    # 1. Tool loop: gọi tool rồi trả lời
    provider = WikiThenAnswer()
    events = drain(streamlit_app.stream_tool_loop(
        provider=provider,
        messages=[{"role": "user", "content": "Cho mình tổng quan trên Wikipedia về blockchain"}],
        tools=TOOLS,
        model="fake-model",
    ))
    kinds = [e["type"] for e in events]
    tool_names = [e["event"]["tool"] for e in events if e["type"] == "tool"]
    finals = [e["text"] for e in events if e["type"] == "final"]

    print("event kinds      :", kinds)
    print("tool names       :", tool_names)
    print("final text       :", finals)

    if tool_names != ["wikipedia"]:
        failures.append(f"tool loop không gọi wikipedia: {tool_names}")
    if not finals or finals[-1] != "Day la cau tra loi tho.":
        failures.append("final text sai")
    # Thu tu stream: tool event phai xuat hien TRUOC final text
    if kinds and kinds[-1] != "final":
        failures.append(f"final phải đến cuối, thứ tự thực tế: {kinds}")
    if "tool" not in kinds or kinds.index("tool") > kinds.index("final"):
        failures.append(f"tool call phải stream trước final text: {kinds}")

    # 2. Tool clarify -> DỪNG, không chạy tiếp
    events2 = drain(streamlit_app.stream_tool_loop(
        provider=ClarifyProvider(),
        messages=[{"role": "user", "content": "Tóm tắt 5 tweet mới nhất"}],
        tools=TOOLS,
        model="fake-model",
    ))
    finals2 = [e["text"] for e in events2 if e["type"] == "final"]
    print("clarify kinds    :", [e["type"] for e in events2])
    print("clarify question :", finals2)

    if len(finals2) != 1:
        failures.append("clarify phải kết thúc bằng 1 final event")
    elif "Ban la ai?" not in finals2[0]:
        failures.append("clarify không trả về câu hỏi")
    # Phai dung ngay sau 1 tool event, khong co vong goi model thu hai
    if len(events2) != 2:
        failures.append(f"clarify phải dừng ngay sau tool call, nhưng có {len(events2)} event")

    # 3. chunk_text: tách chuỗi thành các đoạn, nối lại ra đúng chuỗi gốc
    text = "Xin chao! Day la cau tra loi dai mot vai hang chuc ky tu de kiem tra chunking."
    chunks = list(streamlit_app.chunk_text(text, size=10))
    print("chunks           :", len(chunks))
    if "".join(chunks) != text:
        failures.append("chunk_text không giữ nguyên nội dung")
    if list(streamlit_app.chunk_text("", size=10)):
        failures.append("chunk_text chuỗi rỗng phải trả về rỗng")

    # 4. Transcript: ghi và đọc lại được
    transcript_path = streamlit_app.new_transcript_path("v3", "openrouter")
    streamlit_app.write_transcript(transcript_path, {
        "transcript_id": transcript_path.stem,
        "provider": "openrouter",
        "turns": [],
    })
    print("transcript path  :", transcript_path.name, "exists =", transcript_path.is_file())
    if not transcript_path.is_file():
        failures.append("không ghi được transcript")
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
