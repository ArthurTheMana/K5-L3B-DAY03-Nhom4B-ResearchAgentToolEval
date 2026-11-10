# -*- coding: utf-8 -*-
"""Dump cay DOM thuc te cua app.py ( dung AppTest ) de kiem tra thu tu render.

Chay:
    python scripts/dump_dom.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402

import providers  # noqa: E402
from providers.base import ModelResponse, ToolCall  # noqa: E402


class FakeProvider:
    default_model = "fake-model"

    def __init__(self) -> None:
        self.n = 0

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
        self.n += 1
        if self.n % 2 == 1:
            return ModelResponse(
                text="",
                tool_calls=[ToolCall(name="wikipedia", args={"query": "Blockchain", "lang": "vi"})],
            )
        return ModelResponse(text="Cau tra loi cuoi cung.", tool_calls=[])


def walk(node, out=None, depth=0):
    if out is None:
        out = []
    for child in (getattr(node, "children", {}) or {}).values():
        t = getattr(child, "type", "?")
        if t == "chat_message":
            out.append(("  " * depth) + f"[chat_message name={getattr(child, 'name', '?')}]")
        elif t == "markdown":
            val = str(getattr(child, "value", "")).replace("\n", " ")[:52]
            out.append(("  " * depth) + f"markdown: {val}")
        elif t == "expander":
            out.append(("  " * depth) + f"expander: {getattr(child, 'label', '?')}")
        elif t == "caption":
            out.append(("  " * depth) + f"caption: {str(getattr(child, 'value', ''))[:52]}")
        elif t == "json":
            out.append(("  " * depth) + "json: <args>")
        elif t in {"container", "block", "column"}:
            out.append(("  " * depth) + f"({t})")
        else:
            out.append(("  " * depth) + f"<{t}>")
        walk(child, out, depth + 1)
    return out


def main() -> int:
    providers.make_provider = lambda name: FakeProvider()  # type: ignore[assignment]

    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()
    at.chat_input[0].set_value("Cho mình tổng quan về blockchain").run()

    print("=== DOM sau luot 1 ===")
    for line in walk(at.main):
        print(line)

    print()
    print("=== so chat_message:", len(at.chat_message))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
