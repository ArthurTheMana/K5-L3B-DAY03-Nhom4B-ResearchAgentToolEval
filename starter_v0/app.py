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
* Không phụ thuộc FastAPI/uvicorn — đây là app Streamlit độc lập.
* Mỗi tool call hiện thành card mở rộng: tên tool, args, và kết quả thật.
* Tool `clarify` trả `awaiting_user: True` -> app dừng vòng lặp và chờ người
  dùng trả lời ở lượt sau, đúng như `chat.py`.
* Mỗi phiên chat được ghi ra `transcripts/<...>.transcript.json` — cùng định
  dạng với `chat.py` nên dùng làm bằng chứng cho rubric C6.

Nhóm còn có UI thứ hai dùng OpenUI Lang (React):
    uvicorn ui_server:app --port 8000
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

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
# Tool loop — copy logic tu chat.py (nguon chuan cua starter)
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


def run_tool_loop(
    *,
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
) -> dict[str, Any]:
    """Chay toi da 4 vong tool. Tra ve status + text + danh sach tool event."""
    working = list(messages)
    events: list[dict[str, Any]] = []
    rounds: list[dict[str, Any]] = []

    for round_index in range(1, MAX_TOOL_ROUNDS + 1):
        response = provider.complete(working, tools, model=model, temperature=0.0)
        calls = response.tool_calls

        if not calls:
            rounds.append({"round": round_index, "assistant_text": response.text or "", "tool_calls": []})
            return {
                "status": "answered",
                "assistant_text": response.text or "",
                "tool_events": events,
                "rounds": rounds,
            }

        rounds.append({
            "round": round_index,
            "assistant_text": response.text or "",
            "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
        })
        working.append(assistant_tool_message(response.text, calls))

        non_clarify: list[dict[str, Any]] = []
        for call in calls:
            event = execute_tool_call(call)
            events.append(event)

            result = event.get("result", {})
            # Tool `clarify` danh dau `awaiting_user: True` -> DUNG va cho user tra loi.
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Ban bo sung them thong tin nhe."
                return {
                    "status": "waiting_for_user",
                    "assistant_text": question,
                    "tool_events": events,
                    "rounds": rounds,
                }

            non_clarify.append(event)

        working.append(tool_results_message(non_clarify))

    return {
        "status": "max_tool_rounds",
        "assistant_text": f"Stopped after {MAX_TOOL_ROUNDS} tool rounds.",
        "tool_events": events,
        "rounds": rounds,
    }


# ---------------------------------------------------------------------------
# Transcript (cung format voi chat.py)
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
    version_label = st.text_input("Version label", value="v3", help="Nhan sanh artifacts, vd v3")
    show_raw = st.checkbox("Hien thi raw tool result", value=False)

    key_env = PROVIDER_KEYS.get(provider_name)
    if key_env:
        if os.getenv(key_env):
            st.success(f"{key_env} da duoc cau hinh")
        else:
            st.warning(f"Thieu {key_env}. Hay copy .env.example thanh .env va dien key.")

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
st.caption("Chon tool, chay tool that, luu log, toi uu prompt theo tung version.")

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
    st.error(f"Khong doc duoc artifacts: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "transcript_path" not in st.session_state:
    st.session_state.transcript_path = None

# --- Render lich su ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for event in msg.get("tool_events", []):
            with st.expander(f"🔧 {event.get('tool', '?')}"):
                st.json(event.get("args", {}))
                if show_raw:
                    st.json(event.get("result", {}))

# --- Input ---
prompt = st.chat_input("Cau hoi cua ban...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "tool_events": []})

    try:
        provider = make_provider(provider_name)
        model = getattr(provider, "default_model", None)
    except Exception as exc:
        st.error(f"Khoi tao provider that bai: {exc}")
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
    with st.chat_message("assistant"):
        with st.spinner("Dang chay agent..."):
            try:
                result = run_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                )
            except Exception as exc:
                result = {
                    "status": "provider_error",
                    "assistant_text": f"Loi provider: {type(exc).__name__}: {exc}",
                    "tool_events": [],
                    "rounds": [],
                }

        for event in result["tool_events"]:
            with st.expander(f"🔧 {event.get('tool', '?')}"):
                st.json(event.get("args", {}))
                if show_raw:
                    st.json(event.get("result", {}))

        st.markdown(result["assistant_text"])
        if result["status"] == "waiting_for_user":
            st.info("Agent da hoi lai — cho user tra loi o luot tiep theo.")
        elif result["status"] == "max_tool_rounds":
            st.warning(f"Da het {MAX_TOOL_ROUNDS} vong tool.")

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
        st.warning(f"Khong ghi duoc transcript: {exc}")

    st.rerun()

st.divider()
st.caption("Chay local: `cd starter_v0 && streamlit run app.py` → http://localhost:8501")
st.caption(
    "Link dung thu cho team khac: `cloudflared tunnel --url http://localhost:8501` "
    "(link trycloudflare.com tam thoi, song theo phien cloudflared)."
)
