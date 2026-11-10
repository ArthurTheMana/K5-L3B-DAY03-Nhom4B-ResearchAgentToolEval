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
|   1 | Vương Quang Thắng | 2A202603855 | vuongquangthang0311@gmail.com | vuongquangthang | Prompt & tool declaration — sửa `system_prompt.md` + `tools.yaml` qua v1→v3 |
|   2 | Nguyễn Tài minh Huy | 2A202603828 |        |        | Tool mới + unit test — `wikipedia` |
|   3 |  |  |        |        | Nhóm trưởng — setup, chạy v0–v3, `version_log.csv`, gom bài |
|   4 | Vũ Văn Trường | 2A202603910 | tini.vu.0@gmail.com | `Sz3RO` | Eval nhóm + UI + demo — 10 eval case, UI FastAPI + OpenUI, transcript, báo cáo |


## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.


Báo cáo cá nhân: [2A202603910_VuVanTruong.md](report/team/2A202603910_VuVanTruong.md) · 
[2A202603828_NguyenTaiMinhHuy.md](report/team/2A202603828_NguyenTaiMinhHuy.md)
Vương Quang Thắng : [2A202603855_VuongQuangThang.md](report/team/2A202603855_VuongQuangThang.md)
-

---

## Vũ Văn Trường — 2A202603910

### Phần việc phụ trách

- **CP4 — Eval của nhóm:** viết 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn), phủ đủ 6 loại `failure_type`, có 3 case kiểm tra route tới tool mới `wikipedia`.
- **CP5 — UI:** xây `starter_v0/ui_server.py` (FastAPI + SSE) và `starter_v0/ui/` (React + OpenUI Lang, không cần build step).
- **CP5 — Live chat & báo cáo:** 3 transcript trong `starter_v0/transcripts/`, Phần A của báo cáo nhóm, `report/team/poster.html`, hỗ trợ điền Phần B (B1–B5a, mục 3/5/6/7/8).

### Đóng góp cụ thể

- Viết bộ 10 eval case dựa trên phân tích 6 case FAIL của run v0; sửa lại case G08 sau khi đọc code `run_eval.py` (so sánh args theo kiểu *subset*, tool gọi thừa cũng bị tính FAIL).
- Thiết kế UI theo kiến trúc **2 pha** để hành vi agent trên UI y hệt hành vi được chấm điểm trong eval (phần trình bày OpenUI tách khỏi phần agent, không gộp vào `system_prompt.md`).
- Viết `scripts/test_ui_server.py` (6 unit test) và `scripts/smoke_ui.py` — không cần API key, không gọi mạng.
- Phát hiện và sửa 3 lỗi thật trong lúc làm UI: `SectionItem` đặt sai chỗ làm mất nội dung, chủ đề sáng/tối của OpenUI bị đảo, rule trong script sinh prompt bị `promptOptions` ghi đè.
- Chạy thật bộ eval nhóm: **10/10 PASS** (`provider_error_cases = 0`, `measured_cases = 10/10`).

### Bằng chứng

- File: `starter_v0/data/eval_group.json`, `starter_v0/ui_server.py`, `starter_v0/ui/`, `starter_v0/scripts/test_ui_server.py`, `starter_v0/runs/v3_B_group_openrouter_20261110T184843874713.json`, `starter_v0/transcripts/`, `report/team/group_report.md`, `report/team/poster.html`.
- Commit: `8d63909`, `d917ebe`, `4e3ed92`, `d4f844a`, `83e16aa`, `cfeff3a`.
- Số liệu: `pytest` 90 passed / 0 failed · `test_ui_server.py` 6/6 PASS · run nhóm `case_accuracy = 1.00` · UI đã kiểm chứng end-to-end với tool `wikipedia` trả dữ liệu thật.
- Công cụ AI đã dùng: trợ lý AI hỗ trợ đọc code, thiết kế và viết code/test/báo cáo. Mọi kết quả đều được tôi tự kiểm tra bằng lệnh thật (`pytest`, `run_eval.py`, unit test backend) và ảnh chụp màn hình, không dựa vào lời AI. Chi tiết ở [báo cáo cá nhân](report/team/2A202603910_VuVanTruong.md).

---

## Vương Quang Thắng — 2A202603855

### Phần việc phụ trách

- Sửa `starter_v0/artifacts/system_prompt.md` (v1) và `starter_v0/artifacts/tools.yaml` (v2, v3).

### Đóng góp cụ thể

- Bỏ 4 chỉ dẫn xấu có sẵn của starter, thêm routing rule, viết lại `description` tool theo mẫu "dùng khi / không dùng cho", quy ước args, boundary xác nhận cho `send`.

### Bằng chứng

- Commit `7b1554e` (system prompt v1), `bea3c4a` (v2: tools), `ae1a7d3` (update tools); run `v1`/`v2` trong `starter_v0/runs/`.

---

## Nguyễn Tài minh Huy — 2A202603828

### Phần việc phụ trách

- Viết tool mới `wikipedia` và unit test.

### Đóng góp cụ thể

- Tool `wikipedia` tra cứu kiến thức nền trên Wikipedia REST API, không cần API key, trả error dict thay vì raise; 3 unit test trong `starter_v0/tests/test_tools_todo.py`.

### Bằng chứng

- File `starter_v0/tools/wikipedia/`, commit `33fa5c7`; báo cáo cá nhân `report/team/2A202603828_NguyenTaiMinhHuy.md`.

---

## Bản đồ đóng góp theo vai trò

| Vai trò | Phần việc | File sở hữu chính | Commit tiêu biểu |
|---|---|---|---|
| **A** — Nhóm trưởng | Setup, chạy base eval v0–v3, ghi `version_log.csv`, bảng B1/B2, gom bài | `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/v0..v3_*.json` | `ebe51ea` (CP1 baseline v0), `dcfc738` (v1), `3b2a959` (v2), `c2955ec` (v3) |
| **B** — Prompt & tool declaration | Sửa `system_prompt.md` (v1) và `tools.yaml` (v2, v3): bỏ chỉ dẫn xấu của starter, thêm routing rule, viết lại `description` theo "khi nào dùng / không dùng", quy ước args, boundary `send` | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml` | `7b1554e` (system prompt v1), `bea3c4a` (v2: tools), `ae1a7d3` (update tools) |
| **C** — Tool mới + unit test | Viết tool `wikipedia` (tra cứu kiến thức nền, không cần API key), đăng ký registry, 3 unit test | `starter_v0/tools/wikipedia/`, `starter_v0/tools/__init__.py`, `starter_v0/tests/test_tools_todo.py` | `33fa5c7` (add new tool) |
| **D** — Eval nhóm + UI + demo | 10 eval case, UI FastAPI + OpenUI Lang, 3 transcript live chat, Phần A + poster, hỗ trợ Phần B | `starter_v0/data/eval_group.json`, `starter_v0/ui_server.py`, `starter_v0/ui/`, `starter_v0/transcripts/`, `report/team/` | `83e16aa` (UI + eval), `4e3ed92` (group run 10/10 + transcript), `d4f844a` (fix UI) |
