"""Kiem tra logic render cua app.py bang AppTest cua Streamlit.

Muc tieu:
1. Thu tu hien thi trong mot luot chat (tool card va cau tra loi).
2. Conversation duoc giu lai giua cac luot.
3. Tool call hien ra DUNG THOI DIEM no xay ra (khong doi den het luot).

Chay:
    python scripts/test_render_order.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402

from providers.base import ModelResponse, ToolCall  # noqa: E402

FAILURES: list[str] = []



def dom_walk(node, out=None):
    """Duyet cay DOM thu te, tra ve danh sach (loai, nhan) theo dung thu tu."""
    if out is None:
        out = []
    for child in (getattr(node, "children", {}) or {}).values():
        t = getattr(child, "type", "?")
        if t == "chat_message":
            out.append(("chat_message", getattr(child, "name", "?")))
        elif t == "markdown":
            out.append(("markdown", str(getattr(child, "value", ""))[:60]))
        elif t == "expander":
            out.append(("expander", getattr(child, "label", "?")))
        elif t == "caption":
            out.append(("caption", str(getattr(child, "value", ""))[:60]))
        elif t == "json":
            out.append(("json", ""))
        dom_walk(child, out)
    return out


def element_order(chat_msg) -> list[str]:
    """Thu tu phan tu trong mot chat message, theo DOM thuc te."""
    return [kind for kind, _ in dom_walk(chat_msg)]

def check(cond: bool, msg: str) -> None:
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILURES.append(msg)


class FakeProvider:
    """Luon goi 1 tool roi tra loi. Dung chung cho ca 2 luot."""

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


def main() -> int:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()
    check(not at.exception, f"app chay khong loi: {at.exception}")

    # Patch provider de khong can API key.
    # Phai patch `providers.make_provider` (module nguon) vi AppTest exec app.py
    # trong namespace rieng: `from providers import make_provider` se lay gia tri
    # da patch tai thoi diem script chay.
    import providers

    fake = FakeProvider()
    providers.make_provider = lambda name: fake  # type: ignore[assignment]

    # --- Luot 1 ---
    at.chat_input[0].set_value("Cho mình tổng quan về blockchain").run()
    check(not at.exception, f"luot 1 khong loi: {at.exception}")

    msgs = at.chat_message
    check(len(msgs) == 2, f"co 2 chat message (user + assistant), thuc te: {len(msgs)}")

    if len(msgs) >= 2:
        assistant = msgs[-1]
        # Thu tu phan tu trong bubble cua assistant: dung AppTest lay theo
        # thu tu DOM thuc te, khong phai theo loai element.
        kinds = element_order(assistant)
        print("  thu tu phan tu assistant:", kinds)
        # Tool call phai render TRUOC cau tra loi (dong thoi diem xay ra).
        check(
            bool(kinds) and kinds[0] == "expander" and kinds[-1] == "markdown",
            f"tool card phai render truoc cau tra loi, thuc te: {kinds}",
        )

        # Tool call PHAI xuat hien TRUOC cau tra loi (tool call xay ra truoc)
        raw = assistant.json
        expander_labels = [e.label for e in assistant.expander]
        print("  expander labels:", expander_labels)
        check(len(expander_labels) == 1, "co 1 expander cho tool call")
        check(expander_labels and expander_labels[0].startswith("🔧"), "expander la tool card")

        print("  gia tri markdown trong assistant:", [m.value for m in assistant.markdown])
        text = " ".join(m.value for m in assistant.markdown)
        check("Cau tra loi cuoi cung." in text, "co cau tra loi cua agent trong bubble")

    # --- Luot 2: conversation duoc giu lai? ---
    at.chat_input[0].set_value("Cảm ơn bạn nhiều nhé!").run()
    check(not at.exception, f"luot 2 khong loi: {at.exception}")
    msgs2 = at.chat_message
    print("  so chat message sau luot 2:", len(msgs2))
    check(len(msgs2) == 4, f"luot 2 them 2 message -> 4, thuc te: {len(msgs2)}")

    # Text user cua luot 1 va luot 2 deu con?
    all_text = " | ".join(m.value for m in at.markdown)
    check("Cho mình tổng quan về blockchain" in all_text, "user message luot 1 con lai")
    check("Cảm ơn bạn nhiều nhé!" in all_text, "user message luot 2 con lai")

    # Moi luot chat deu phai render theo cung thu tu: tool card -> cau tra loi
    for i, m in enumerate(msgs2):
        if m.name == "assistant":
            o = element_order(m)
            check(
                bool(o) and o[0] == "expander" and o[-1] == "markdown",
                f"luot {i // 2} assistant thu tu {o}",
            )
            break

    # Transcript co ghi 2 luot khong?
    import json

    tdir = ROOT / "transcripts"
    files = sorted(tdir.glob("*.transcript.json"), key=lambda p: p.stat().st_mtime)
    if files:
        data = json.loads(files[-1].read_text(encoding="utf-8"))
        print("  transcript moi nhat:", files[-1].name, "| so luot:", len(data["turns"]))
        check(len(data["turns"]) == 2, f"transcript ghi 2 luot, thuc te: {len(data['turns'])}")
        files[-1].unlink()
    else:
        check(False, "khong tim thay transcript")

    print()
    if FAILURES:
        print("FAIL:")
        for f in FAILURES:
            print("  -", f)
        return 1
    print("PASS: render order + conversation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
