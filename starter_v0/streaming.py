"""Streaming token thật cho provider OpenAI-compatible (OpenRouter, OpenAI).

Vì sao cần module riêng?
-----------------------
`providers/` là code của starter. Thêm method mới vào đó không làm hỏng eval,
nhưng để **không đụng vào `providers/`** hoàn toàn, module này tự dựng client
theo đúng cấu hình của provider (`api_key_env`, `base_url`, `default_model`)
và tự parse luồng SSE.

Quan trọng: module này **không thay đổi** `provider.complete()`. `chat.py` và
`run_eval.py` vẫn dùng `complete()` y nguyên, nên **hành vi agent trên UI và
hành vi được chấm điểm trong eval là cùng một logic**.

Luồng trả về (generator):
    {"type": "delta", "text": "..."}          -> thêm một đoạn token
    {"type": "tool_calls", "calls": [...]}    -> tool call đã gom đủ (cuối luồng)
"""
from __future__ import annotations

import json
import os
from typing import Any, Iterator

from providers.base import ToolCall


class StreamingNotSupported(RuntimeError):
    """Provider này không hỗ trợ streaming token -> caller dùng lại complete()."""


def _build_client(provider: Any) -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover
        raise StreamingNotSupported("Thiếu package `openai`.") from exc

    api_key = os.getenv(getattr(provider, "api_key_env", "")) or getattr(provider, "api_key_default", None)
    if not api_key:
        raise StreamingNotSupported(f"Thiếu API key: {getattr(provider, 'api_key_env', '?')}")

    return OpenAI(api_key=api_key, base_url=getattr(provider, "base_url", None))


def _is_openai_compatible(provider: Any) -> bool:
    """Chỉ provider OpenAI-compatible mới dùng được `stream=True`."""
    return hasattr(provider, "api_key_env") and hasattr(provider, "base_url")


def stream_complete(
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]] | None = None,
    *,
    model: str | None = None,
    temperature: float = 0.0,
) -> Iterator[dict[str, Any]]:
    """Stream token thật từ API. Raise `StreamingNotSupported` nếu không được."""
    if not _is_openai_compatible(provider):
        raise StreamingNotSupported("Provider không tương thích OpenAI streaming.")

    client = _build_client(provider)
    kwargs: dict[str, Any] = {
        "model": model or getattr(provider, "default_model", None),
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    if tools:
        kwargs["tools"] = tools

    stream = client.chat.completions.create(**kwargs)

    # Gom tool call: mỗi tool call có thể tới nhiều chunk, phải nối lại.
    slots: dict[int, dict[str, str]] = {}
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if getattr(delta, "content", None):
            yield {"type": "delta", "text": delta.content}
        for call in getattr(delta, "tool_calls", None) or []:
            slot = slots.setdefault(call.index, {"name": "", "args": ""})
            if getattr(call, "id", None) and not slot["name"]:
                pass
            fn = getattr(call, "function", None)
            if fn is None:
                continue
            if fn.name:
                slot["name"] += fn.name
            if fn.arguments:
                slot["args"] += fn.arguments

    if slots:
        calls: list[ToolCall] = []
        for index in sorted(slots):
            slot = slots[index]
            raw_args = slot["args"] or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                # Giữ nguyên hành vi của provider: lỗi JSON args bị chấm sai tham số,
                # không bị coi là provider_error.
                args = {"_invalid_json_arguments": raw_args}
            if not isinstance(args, dict):
                args = {"_invalid_json_arguments": raw_args}
            calls.append(ToolCall(name=slot["name"], args=args))
        yield {"type": "tool_calls", "calls": calls}
