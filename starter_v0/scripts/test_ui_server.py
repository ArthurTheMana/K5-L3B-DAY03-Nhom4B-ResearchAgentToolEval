"""Unit test cho backend FastAPI (vai trò D).

Khong can API key, khong can mang that — dung fake provider.
Chay:
    python scripts/test_ui_server.py
hoac
    pytest scripts/test_ui_server.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

import ui_server  # noqa: E402
from ui_server import wrap_bare_section_items  # noqa: E402


# ---------------------------------------------------------------------------
# wrap_bare_section_items
# ---------------------------------------------------------------------------
PROGRAM_BARE = """root = Card([header, blockchainSection, cryptoSection, followUps], [src1])
header = CardHeader("Tieu de", "phu de")
blockchainSection = SectionItem("blockchain", "Blockchain", [blockchainContent])
blockchainContent = TextContent("Noi dung blockchain")
cryptoSection = SectionItem("crypto", "Cryptocurrency", [cryptoContent])
cryptoContent = TextContent("Noi dung crypto")
followUps = FollowUpBlock([fu1])
fu1 = FollowUpItem("Tiep tuc")
src1 = { title: "Blockchain", sourceName: "Wikipedia", url: "https://en.wikipedia.org/wiki/Blockchain" }"""


def test_bare_section_items_are_wrapped_in_section_block() -> None:
    out = wrap_bare_section_items(PROGRAM_BARE)
    assert "__sectionsBlock = SectionBlock([" in out
    assert "blockchainSection" in out.split("__sectionsBlock = SectionBlock([")[1].split("]")[0]
    assert "cryptoSection" in out.split("__sectionsBlock = SectionBlock([")[1].split("]")[0]
    # Root Card khong con tro truc tiep toi SectionItem nua.
    root_line = [line for line in out.splitlines() if line.strip().startswith("root =")][0]
    assert "SectionItem" not in root_line
    assert "__sectionsBlock" in root_line


def test_program_without_section_items_is_unchanged() -> None:
    program = """root = Card([header, body])
header = CardHeader("Tieu de")
body = TextContent("Noi dung")"""
    assert wrap_bare_section_items(program) == program


def test_section_block_used_correctly_is_unchanged() -> None:
    program = """root = Card([header, sectionsBlock])
header = CardHeader("Tieu de")
sectionsBlock = SectionBlock([s1])
s1 = SectionItem("a", "A", [c1])
c1 = TextContent("noi dung")"""
    assert wrap_bare_section_items(program) == program


def test_split_top_level_ignores_commas_inside_strings() -> None:
    parts = ui_server._split_top_level('a, "x, y", b')
    assert parts == ["a", '"x, y"', "b"]


# ---------------------------------------------------------------------------
# End-to-end voi fake provider
# ---------------------------------------------------------------------------
class FakeProvider:
    """Vong 1: goi tool. Vong 2: tra loi text. Vong 3 (neu co): sinh OpenUI Lang."""

    default_model = "fake-model"

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
        self.calls.append({"n_messages": len(messages), "has_tools": bool(tools)})
        if len(self.calls) == 1:
            from providers.base import ModelResponse, ToolCall

            return ModelResponse(
                text="",
                tool_calls=[ToolCall(name="wikipedia", args={"query": "Blockchain", "lang": "en"})],
            )
        if len(self.calls) == 2:
            from providers.base import ModelResponse

            return ModelResponse(text="Cau tra loi tho cua agent.", tool_calls=[])
        from providers.base import ModelResponse

        return ModelResponse(text=PROGRAM_BARE, tool_calls=[])


def test_chat_stream_emits_all_events() -> None:
    provider = FakeProvider()
    ui_server.make_provider = lambda name: provider  # type: ignore[assignment]
    ui_server._openui_prompt_cache = "prompt openui gia lap"
    client = TestClient(ui_server.app)

    with client.stream(
        "POST",
        "/api/chat",
        json={"message": "Cho mình tổng quan trên Wikipedia về blockchain", "version": "v3"},
    ) as resp:
        assert resp.status_code == 200
        events: list[tuple[str, dict]] = []
        name = ""
        for line in resp.iter_lines():
            if line.startswith("event: "):
                name = line[7:].strip()
            elif line.startswith("data: "):
                import json

                events.append((name, json.loads(line[6:])))

    names = [e for e, _ in events]
    for required in ("start", "tool_call", "tool_result", "answer", "ui", "done"):
        assert required in names, f"thieu event {required}"

    ui_event = next(d for e, d in events if e == "ui")
    assert "__sectionsBlock" in ui_event["text"], "SectionItem chua duoc boc vao SectionBlock"
    assert "root = Card(" in ui_event["text"]


def test_health_and_tools_endpoints() -> None:
    client = TestClient(ui_server.app)
    assert client.get("/api/health").json()["status"] == "ok"
    names = [t["name"] for t in client.get("/api/tools").json()["tools"]]
    assert "lookup" in names
    index = client.get("/")
    assert index.status_code == 200
    assert "__OpenUI" in index.text


def main() -> int:
    failures = []
    for fn in [
        test_bare_section_items_are_wrapped_in_section_block,
        test_program_without_section_items_is_unchanged,
        test_section_block_used_correctly_is_unchanged,
        test_split_top_level_ignores_commas_inside_strings,
        test_chat_stream_emits_all_events,
        test_health_and_tools_endpoints,
    ]:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{fn.__name__}: {type(exc).__name__}: {exc}")
            print(f"FAIL  {fn.__name__}: {exc}")
    print()
    if failures:
        print("FAILED:", len(failures))
        return 1
    print("PASS: ui_server tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
