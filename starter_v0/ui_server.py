"""FastAPI backend cho UI OpenUI của research agent (Day 03 Lab).

Kiến trúc
---------
    Browser (React + OpenUI Lang renderer)
        │  POST /api/chat   {messages: [...], provider, version}
        ▼
    FastAPI (file này)
        │  dùng lại 100% code của starter_v0:
        │    - providers.make_provider()   -> gọi model thật
        │    - tools.TOOL_FUNCTIONS        -> chạy tool thật
        │    - versioning.build_artifact_version -> hash prompt/tools
        ▼
    OpenRouter / Tavily / Firecrawl / RapidAPI / Wikipedia

Điểm quan trọng
---------------
* **Agent chạy y hệt `chat.py` / `run_eval.py`.** Pha 1 dùng nguyên văn
  `artifacts/system_prompt.md` + `artifacts/tools.yaml`, nên hành vi chọn tool
  và truyền args trên UI GIỐNG HỆT hành vi được chấm điểm trong eval.
* **OpenUI chỉ là lớp trình bày, không can thiệp agent.** Pha 2 mới sinh
  OpenUI Lang từ kết quả tool + câu trả lời thô. Nhờ vậy prompt 53 KB của
  OpenUI không làm loãng routing mà rubric C2/C3 đo.
* Mỗi tool call được phát ra sự kiện SSE riêng, nên UI hiện được từng bước
  (giống hệt những gì transcript ghi lại).
* Tool `clarify` trả `awaiting_user: True` -> server dừng vòng lặp và trả
  `status: waiting_for_user`, chờ lượt user tiếp theo.

Chạy:
    cd starter_v0
    uvicorn ui_server:app --reload --port 8000
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
UI_DIR = ROOT / "ui"
load_lab_env(ROOT)

MAX_TOOL_ROUNDS = 4
HISTORY_PAIRS = 5

app = FastAPI(title="Research Agent — Day 03 Lab")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSS/JS tinh (app.css) phai duoc serve o duong goc de trang index.html load duoc.
if UI_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")


# ---------------------------------------------------------------------------
# Tool loop — copy logic tu chat.py (nguon chuan cua starter)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Pha 2: render OpenUI Lang
# ---------------------------------------------------------------------------
# Prompt OpenUI Lang duoc sinh offline boi scripts/gen_openui_prompt.mjs
# (node + @openuidev/react-ui). File nay da commit san vao repo nen chay UI
# khong can node/npm.
OPENUI_PROMPT_PATH = UI_DIR / "openui_prompt.md"

_openui_prompt_cache: str | None = None


def openui_prompt() -> str:
    global _openui_prompt_cache
    if _openui_prompt_cache is None:
        if not OPENUI_PROMPT_PATH.is_file():
            return ""
        _openui_prompt_cache = OPENUI_PROMPT_PATH.read_text(encoding="utf-8")
    return _openui_prompt_cache


def render_openui(
    provider: Any,
    raw_answer: str,
    tool_events: list[dict[str, Any]],
    *,
    model: str | None,
) -> str:
    """Bien cau tra loi tho + ket qua tool thanh chuong trinh OpenUI Lang.

    Tra ve chuoi rong neu khong render duoc — frontend se fallback sang hien text thuan.
    """
    prompt = openui_prompt()
    if not prompt or not raw_answer.strip():
        return ""

    context = {
        "answer": raw_answer,
        "tool_results": [
            {"tool": e.get("tool"), "args": e.get("args"), "result": e.get("result")}
            for e in tool_events
        ],
    }

    user_message = (
        "Doi day la ket qua cua research agent cho mot luot hoi.\n\n"
        f"CAU HOI:\n{context['answer']}\n\n"
        f"KET QUA TOOL:\n{json_text(context['tool_results'], max_chars=12000)}\n\n"
        "Hay bien ket qua tren thanh MOT chuong trinh OpenUI Lang hien thi cho nguoi dung. "
        "Chi tra ve chuong trinh OpenUI Lang, khong giai thich them."
    )

    try:
        response = provider.complete(
            [{"role": "system", "content": prompt}, {"role": "user", "content": user_message}],
            None,
            model=model,
            temperature=0.0,
        )
    except Exception:
        return ""

    text = (response.text or "").strip()
    # Chi nhan "answer" (khong phai tool call) va phai la chuong trinh OpenUI.
    if response.tool_calls or not re.search(r"^\s*root\s*=", text, re.MULTILINE):
        return ""
    return text


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
async def index() -> FileResponse:
    """Trang UI (mot file HTML tinh, khong can build step)."""
    html = UI_DIR / "index.html"
    if not html.is_file():
        return JSONResponse({"error": f"UI file not found: {html}"}, status_code=500)
    return FileResponse(html)


@app.get("/api/tools")
async def list_tools() -> dict[str, Any]:
    """Danh sach tool agent dang co (doc tu tools.yaml luc chay)."""
    declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    return {
        "tools": [
            {"name": d.get("name"), "description": d.get("description", ""), "parameters": d.get("parameters", {})}
            for d in declarations
        ],
        "implemented": sorted(TOOL_FUNCTIONS),
    }


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(body: dict[str, Any]) -> StreamingResponse:
    """Chay agent 1 luot va stream SSE: tool_call / tool_result / answer."""
    provider_name = str(body.get("provider") or "openrouter")
    version_label = str(body.get("version") or "v3")
    incoming = body.get("messages") or []
    user_text = str(body.get("message") or "").strip()

    if not user_text and incoming:
        last = incoming[-1]
        user_text = str(last.get("content") or "").strip()
    if not user_text:
        return JSONResponse({"error": "message is required"}, status_code=400)

    try:
        system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
        declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
        openai_tools = to_openai_tools(declarations)
        artifact_version = build_artifact_version(
            version_label, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml"
        )
        provider = make_provider(provider_name)
        model = getattr(provider, "default_model", None)
    except Exception as exc:
        return JSONResponse(
            {"error": f"{type(exc).__name__}: {exc}"}, status_code=500
        )

    history = [
        {"role": m.get("role"), "content": str(m.get("content") or "")}
        for m in incoming
        if m.get("role") in {"user", "assistant"}
    ]
    if history and history[-1]["content"] == user_text:
        history = history[:-1]

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history, HISTORY_PAIRS),
        {"role": "user", "content": user_text},
    ]

    def sse(event: str, data: dict[str, Any]) -> str:
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"

    def stream() -> Any:
        yield sse("start", {"artifact_version": artifact_version.artifact_version, "provider": provider_name, "model": model})

        working = list(messages)
        collected: list[dict[str, Any]] = []
        try:
            for round_index in range(1, MAX_TOOL_ROUNDS + 1):
                response = provider.complete(working, openai_tools, model=model, temperature=0.0)
                calls = response.tool_calls

                if not calls:
                    raw_text = response.text or ""
                    yield sse("answer", {"text": raw_text, "round": round_index})
                    # Pha 2: chuyen cau tra loi tho -> OpenUI Lang (chi lop trinh bay).
                    ui_text = render_openui(provider, raw_text, collected, model=model)
                    if ui_text:
                        yield sse("ui", {"text": ui_text})
                    yield sse("done", {"status": "answered"})
                    return

                yield sse("assistant", {"text": response.text or "", "round": round_index})
                working.append(assistant_tool_message(response.text, calls))

                non_clarify: list[dict[str, Any]] = []
                for call in calls:
                    yield sse("tool_call", {"name": call.name, "args": call.args, "round": round_index})
                    event = execute_tool_call(call)
                    yield sse("tool_result", event)
                    collected.append(event)

                    result = event.get("result", {})
                    if isinstance(result, dict) and result.get("awaiting_user"):
                        question = result.get("question") or call.args.get("question") or "Ban bo sung them thong tin nhe."
                        yield sse("answer", {"text": question, "round": round_index, "awaiting_user": True})
                        yield sse("done", {"status": "waiting_for_user"})
                        return

                    non_clarify.append(event)

                working.append(tool_results_message(non_clarify))

            yield sse("answer", {"text": f"Stopped after {MAX_TOOL_ROUNDS} tool rounds.", "round": MAX_TOOL_ROUNDS})
            yield sse("done", {"status": "max_tool_rounds"})
        except Exception as exc:
            yield sse("error", {"message": f"{type(exc).__name__}: {exc}"})
            yield sse("done", {"status": "provider_error"})

    return StreamingResponse(stream(), media_type="text/event-stream")
