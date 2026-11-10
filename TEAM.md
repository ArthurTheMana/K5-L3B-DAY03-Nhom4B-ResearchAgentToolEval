# Team

## Thông tin nhóm

- Tên nhóm: Nhom4B
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
  - Repo: https://github.com/ArthurTheMana/K5-L3B-DAY03-Nhom4B-ResearchAgentToolEval
  - Nhánh nộp: `main`
  - Commit chốt: `d4f844a`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Vương Quang Thắng | 2A202603855 |        |        | B — Prompt & tool declaration (sửa `system_prompt.md` + `tools.yaml` qua v1→v3) |
|   2 | Nguyễn Tài minh Huy | 2A202603828 |        |        | C — Tool mới + unit test (`wikipedia`) |
|   3 |  |  |        |        | A — Nhóm trưởng (setup, chạy v0–v3, `version_log.csv`, gom bài) |
|   4 |  |  |        | `Sz3RO` | D — Eval nhóm + UI + demo (10 eval case, UI FastAPI + OpenUI, transcript, báo cáo) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## HoVaTen-MSSV

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

---

## Bản đồ đóng góp theo vai trò

| Vai trò | Phần việc | File sở hữu chính | Commit tiêu biểu |
|---|---|---|---|
| **A** — Nhóm trưởng | Setup, chạy base eval v0–v3, ghi `version_log.csv`, bảng B1/B2, gom bài | `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/v0..v3_*.json` | `ebe51ea` (CP1 baseline v0), `dcfc738` (v1), `3b2a959` (v2), `c2955ec` (v3) |
| **B** — Prompt & tool declaration | Sửa `system_prompt.md` (v1) và `tools.yaml` (v2, v3): bỏ chỉ dẫn xấu của starter, thêm routing rule, viết lại `description` theo "khi nào dùng / không dùng", quy ước args, boundary `send` | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml` | `7b1554e` (system prompt v1), `bea3c4a` (v2: tools), `ae1a7d3` (update tools) |
| **C** — Tool mới + unit test | Viết tool `wikipedia` (tra cứu kiến thức nền, không cần API key), đăng ký registry, 3 unit test | `starter_v0/tools/wikipedia/`, `starter_v0/tools/__init__.py`, `starter_v0/tests/test_tools_todo.py` | `33fa5c7` (add new tool) |
| **D** — Eval nhóm + UI + demo | 10 eval case, UI FastAPI + OpenUI Lang, 3 transcript live chat, Phần A + poster, hỗ trợ Phần B | `starter_v0/data/eval_group.json`, `starter_v0/ui_server.py`, `starter_v0/ui/`, `starter_v0/transcripts/`, `report/team/` | `83e16aa` (UI + eval), `4e3ed92` (group run 10/10 + transcript), `d4f844a` (fix UI) |
