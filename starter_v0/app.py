"""UI Streamlit cho research agent (Day 03 Lab).

Chạy:
    cd starter_v0
    streamlit run app.py          # -> http://localhost:8501

Đặc điểm
---------
* Tool loop được **copy nguyên văn** từ `chat.py` (nguồn chuẩn của starter), nên
  hành vi chọn tool / truyền args trên UI **giống hệt** hành vi được chấm điểm
  trong eval (`run_eval.py` chạy cùng một logic với `artifacts/system_prompt.md`
  và `artifacts/tools.yaml`).
* **Streaming ở tầng sự kiện**: mỗi tool call hiện ra *ngay khi agent vừa gọi*,
  không phải đợi cả lượt xong mới hiện. Xem `stream_tool_loop()`.
* Tool `clarify` trả `awaiting_user: True` -> app dừng vòng lặp và chờ người
  dùng trả lời ở lượt sau, đúng như `chat.py`.
* Mỗi phiên chat được ghi ra `transcripts/<...>.transcript.json` — cùng định
  dạng với `chat.py` nên dùng làm bằng chứng cho rubric C6.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations
from versioning import build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

MAX_TOOL_ROUNDS = 4
HISTORY_PAIRS = 5

PROVIDER_KEYS: dict[str, str | None] = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "ollama": None,
}

st.set_page_config(page_title="Research Agent — Day 03 Lab", layout="centered")


# ---------------------------------------------------------------------------
# Tool loop — copy logic từ chat.py (nguồn chuẩn của starter)
# ---------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def json_text(value: Any, *, max_chars: int | None = None) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No local implementation for {call.name}"},
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict[str, str]:
    call_summary = [{"name": call.name, "args": call.args} for call in calls]
    content = response_text or "I will call the selected tool(s)."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json_text(call_summary)}",
    }


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json_text(events, max_chars=24000)}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def trim_history(history: list[dict[str, str]], window: int) -> list[dict[str, str]]:
    if window <= 0:
        return []
    return history[-window * 2:]


def stream_tool_loop(
    *,
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
) -> Iterator[dict[str, Any]]:
    """Chạy tool loop và **yield từng sự kiện ngay khi nó xảy ra**.

    Yield:
        {"type": "delta", "text": "..."}     -> thêm một đoạn token của câu trả lời
        {"type": "tool",  "event": {...}}    -> vừa gọi xong 1 tool
        {"type": "final", "text": "..."}     -> câu trả lời cuối cùng

    Ưu tiên **streaming token thật** (`streaming.stream_complete`). Provider không
    hỗ trợ thì tự động lùi về `provider.complete()` — logic tool call giống hệt
    `chat.py` nên hành vi không đổi.
    """
    working = list(messages)
    events: list[dict[str, Any]] = []

    for _round_index in range(1, MAX_TOOL_ROUNDS + 1):
        calls: list[ToolCall] = []
        text_parts: list[str] = []
        for ev in _one_round(provider, working, tools, model):
            if ev["type"] == "delta":
                text_parts.append(ev["text"])
                yield {"type": "delta", "text": ev["text"]}
            elif ev["type"] == "tool_calls":
                calls = ev["calls"]
        text = "".join(text_parts)

        if not calls:
            yield {"type": "final", "text": text}
            return

        working.append(assistant_tool_message(text, calls))
        non_clarify: list[dict[str, Any]] = []

        for call in calls:
            event = execute_tool_call(call)
            events.append(event)
            # Yield ngay: UI hiện card của tool call này trước khi model trả lời.
            yield {"type": "tool", "event": event}

            result = event.get("result", {})
            # Tool `clarify` đánh dấu `awaiting_user: True` -> DỪNG và chờ user trả lời.
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                yield {"type": "final", "text": question}
                return

            non_clarify.append(event)

        working.append(tool_results_message(non_clarify))

    yield {"type": "final", "text": f"Đã dừng sau {MAX_TOOL_ROUNDS} vòng tool."}


def _one_round(
    provider: Any,
    working: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
) -> Iterator[dict[str, Any]]:
    """Gọi model một vòng, yield từng đoạn token nếu provider hỗ trợ.

    Yield:
        {"type": "delta", "text": "..."}        -> một đoạn token
        {"type": "tool_calls", "calls": [...]}  -> tool call đã gom đủ
    """
    try:
        from streaming import StreamingNotSupported, stream_complete
    except ImportError:
        StreamingNotSupported = RuntimeError  # type: ignore[assignment,misc]
        stream_complete = None  # type: ignore[assignment]

    if stream_complete is not None:
        try:
            for ev in stream_complete(provider, working, tools, model=model, temperature=0.0):
                yield ev
            return
        except StreamingNotSupported:
            pass

    # Provider không hỗ trợ streaming -> gọi blocking như cũ.
    response = provider.complete(working, tools, model=model, temperature=0.0)
    if response.text:
        yield {"type": "delta", "text": response.text}
    if response.tool_calls:
        yield {"type": "tool_calls", "calls": response.tool_calls}


def render_tool_event(container: Any, event: dict[str, Any], show_raw: bool) -> None:
    """Hien 1 tool call dang card.

    Dung chung cho ca luoc streaming (container = vung tool) va lich su
    (container = None) de hai noi luon ra CUNG thu tu va cung hinh thuc.
    """
    target = container if container is not None else st
    with target.expander(f"🔧 {event.get('tool', '?')}"):
        st.json(event.get("args", {}))
        summary = summarize_result(event.get("result", {}))
        if summary:
            st.caption(summary)
        if show_raw:
            st.json(event.get("result", {}))


def summarize_result(result: Any) -> str:
    """Tom tat ngan ket qua tool de nguoi dung khong phai mo expander."""
    if not isinstance(result, dict):
        return ""
    if result.get("awaiting_user"):
        return "⏸ Đang chờ bạn trả lời."
    if result.get("error"):
        return f"⚠️ Lỗi: {result.get('message') or result.get('error')}"
    items = result.get("items")
    if isinstance(items, list) and items:
        titles = [str(i.get("title")) for i in items[:5] if isinstance(i, dict) and i.get("title")]
        if titles:
            more = f" (+{len(items) - len(titles)} mục)" if len(items) > len(titles) else ""
            return "📄 " + ", ".join(titles) + more
    if result.get("text"):
        return "📄 " + str(result["text"])[:160].replace("\n", " ")
    return ""


def chunk_text(text: str, size: int = 48) -> Iterator[str]:
    """Chia câu trả lời thành các đoạn nhỏ để `st.write_stream` hiện dần.

    Lưu ý: đây chỉ là streaming ở *tầng hiển thị*. Provider của starter chỉ expose
    `complete()` (không có API token-streaming), nên model đã sinh xong câu trả lời
    trước khi UI bắt đầu hiện. Mọi thứ *đúng* thời điểm xảy ra — tool call — đã
    được stream thật ở trên.
    """
    if not text:
        return
    for start in range(0, len(text), size):
        yield text[start:start + size]
        time.sleep(0.012)
# ---------------------------------------------------------------------------
# Transcript (cùng format với chat.py)
# ---------------------------------------------------------------------------
def write_transcript(path: Path, transcript: dict[str, Any]) -> None:
    transcript["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def new_transcript_path(version: str, provider: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return TRANSCRIPTS_DIR / f"{version}_{provider}_{stamp}.transcript.json"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def load_tools() -> list[dict[str, Any]]:
    try:
        return load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    except Exception:
        return []


with st.sidebar:
    st.title("Research Agent")
    st.caption("Day 03 Lab · Tool Eval")

    provider_name = st.selectbox("Provider", list(PROVIDER_KEYS), index=0)
    version_label = st.text_input("Version label", value="v3", help="Nhãn sánh artifacts, vd v3")
    show_raw = st.checkbox("Hiển thị raw tool result", value=False)

    key_env = PROVIDER_KEYS.get(provider_name)
    if key_env:
        if os.getenv(key_env):
            st.success(f"{key_env} đã được cấu hình")
        else:
            st.warning(f"Thiếu {key_env}. Hãy copy .env.example thành .env và điền key.")

    if st.button("Reset chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.transcript_path = None
        st.rerun()

    st.divider()
    tools_list = load_tools()
    st.subheader(f"Tools ({len(tools_list)})")
    for decl in tools_list:
        with st.expander(decl.get("name", "?")):
            st.caption(decl.get("description", ""))
            params = decl.get("parameters", {}).get("properties", {})
            if params:
                st.json(params)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
st.title("Research Agent")
st.caption("Chọn tool, chạy tool thật, lưu log, tối ưu prompt theo từng version.")

try:
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": item["name"],
                "description": item.get("description", ""),
                "parameters": item.get("parameters", {"type": "object", "properties": {}}),
            },
        }
        for item in declarations
    ]
    artifact_version = build_artifact_version(
        version_label, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml"
    )
except Exception as exc:
    st.error(f"Không đọc được artifacts: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "transcript_path" not in st.session_state:
    st.session_state.transcript_path = None

# --- Render lịch sử ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Tool call truoc, cau tra loi sau — giong het thu tu khi streaming.
        for event in msg.get("tool_events", []):
            render_tool_event(None, event, show_raw)
        st.markdown(msg["content"])

# --- Input ---
prompt = st.chat_input("Câu hỏi của bạn...")

if prompt:
    # Bubble của lượt hiện tại: vòng render lịch sử đã chạy xong trước đó nên
    # lượt này chưa được vẽ từ session_state — phải vẽ thủ công, nếu không
    # người dùng sẽ không thấy câu hỏi của mình cho tới lượt sau.
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt, "tool_events": []})

    try:
        provider = make_provider(provider_name)
        model = getattr(provider, "default_model", None)
    except Exception as exc:
        st.error(f"Khởi tạo provider thất bại: {exc}")
        st.session_state.messages.pop()
        st.rerun()

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
        if m["role"] in {"user", "assistant"}
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history, HISTORY_PAIRS),
        {"role": "user", "content": prompt},
    ]

    started_at = now_iso()
    tool_events: list[dict[str, Any]] = []
    final_text = ""
    status = "answered"

    with st.chat_message("assistant"):
        # Tool call hiện NGAY khi agent vừa gọi (streaming theo sự kiện).
        tool_area = st.container()

        # Dòng trạng thái: hiện NGAY lập tức kể cả khi model còn đang suy nghĩ,
        # để người dùng không phải nhìn một bubble rỗng đứng yên.
        status_line = st.empty()
        status_line.info("⏳ Đang gọi model…")

        # Vùng hiển thị câu trả lời, cập nhật dần theo token.
        answer_slot = st.empty()
        streamed_text = ""

        try:
            for ev in stream_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model,
            ):
                if ev["type"] == "delta":
                    streamed_text += ev["text"]
                    answer_slot.markdown(streamed_text)
                elif ev["type"] == "tool":
                    event = ev["event"]
                    tool_events.append(event)
                    status_line.info(f"🔧 Đang chạy tool `{event.get('tool', '?')}`…")
                    render_tool_event(tool_area, event, show_raw)
                    status_line.info("⏳ Đang gọi model…")
                elif ev["type"] == "final":
                    final_text = ev["text"]
                    if ev["text"].startswith(f"Đã dừng sau {MAX_TOOL_ROUNDS}"):
                        status = "max_tool_rounds"
        except Exception as exc:
            status = "provider_error"
            final_text = f"Lỗi provider: {type(exc).__name__}: {exc}"

        # Dòng trạng thái đã hết việc -> xoá đi.
        status_line.empty()

        # Câu trả lời cuối cùng (bổ sung phần nếu vòng cuối không stream được).
        if final_text and final_text != streamed_text:
            answer_slot.markdown(final_text)
        elif not final_text:
            answer_slot.markdown(streamed_text)

        if any(
            isinstance(e.get("result"), dict) and e["result"].get("awaiting_user")
            for e in tool_events
        ):
            status = "waiting_for_user"
            st.info("Agent đã hỏi lại — chờ user trả lời ở lượt tiếp theo.")
        elif status == "max_tool_rounds":
            st.warning(f"Đã hết {MAX_TOOL_ROUNDS} vòng tool.")

    result = {
        "status": status,
        "assistant_text": final_text,
        "tool_events": tool_events,
        "rounds": [],
    }

    st.session_state.messages.append(
        {"role": "assistant", "content": result["assistant_text"], "tool_events": result["tool_events"]}
    )

    # --- Ghi transcript ---
    try:
        path = st.session_state.transcript_path
        if path is None:
            path = new_transcript_path(version_label, provider_name)
            st.session_state.transcript_path = path
            write_transcript(path, {
                "transcript_id": path.stem,
                **artifact_version.__dict__,
                "provider": provider_name,
                "model": model,
                "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
                "tools": str(ARTIFACTS_DIR / "tools.yaml"),
                "history_window": HISTORY_PAIRS,
                "max_tool_rounds": MAX_TOOL_ROUNDS,
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "turns": [],
            })
        transcript = json.loads(path.read_text(encoding="utf-8"))
        transcript["turns"].append({
            "turn_index": len(transcript["turns"]) + 1,
            "started_at": started_at,
            "ended_at": now_iso(),
            "user": prompt,
            "status": result["status"],
            "assistant_text": result["assistant_text"],
            "rounds": result.get("rounds", []),
            "tool_events": result["tool_events"],
        })
        write_transcript(path, transcript)
    except Exception as exc:
        st.warning(f"Không ghi được transcript: {exc}")

    # KHÔNG gọi st.rerun() ở đây.
    # st.rerun() sẽ xoá toàn bộ output vừa stream, dựng lại từ session_state
    # (lật thứ tự phần tử) và nhảy trang về đầu — người dùng mất context.
    # Lượt chat vừa rồi đã nằm trong session_state nên lượt sau sẽ hiển thị lại
    # đúng thứ tự nhờ render_tool_event dùng chung.
