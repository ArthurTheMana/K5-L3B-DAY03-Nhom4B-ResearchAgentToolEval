# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> Research agent: nhận câu hỏi của người dùng, chọn đúng tool, chạy tool thật (tìm web, đọc URL, tra tweet theo tài khoản hoặc từ khóa, tra cứu Wikipedia, tìm paper arXiv), rồi tổng hợp kết quả thành digest có trích dẫn. Khi thiếu thông tin agent hỏi lại thay vì đoán bừa, và khi đăng bản tin lên Telegram luôn hỏi xác nhận trước khi gửi.

**Cách chạy UI:**

> ```bash
> cd starter_v0
> pip install -r requirements.txt
> uvicorn ui_server:app --port 8000     # → http://127.0.0.1:8000
> ```
> UI là **FastAPI (Python) + OpenUI Lang**: backend chạy research agent thật (tái dùng nguyên code của `starter_v0`), frontend render kết quả bằng component OpenUI (bảng, card, callout, chart). Dependency đã thêm vào `starter_v0/requirements.txt`: `fastapi>=0.110.0`, `uvicorn[standard]>=0.27.0`.

**Link dùng thử (deploy):**

> Deploy nhanh bằng Cloudflare Tunnel: chạy UI local (`uvicorn ui_server:app --port 8000`), cài `cloudflared`, rồi `cloudflared tunnel --url http://localhost:8000` → copy URL `https://<random>.trycloudflare.com` dán vào dòng dưới. Link này tạm thời, sống theo phiên `cloudflared` nên phải giữ terminal mở trong suốt buổi demo.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin, dừng chờ trả lời ở lượt sau | không |
| timeline | lấy các bài đăng gần đây của một tài khoản theo `screenname` | không |
| social_search | tìm bài đăng theo từ khóa, có `search_type` Latest/Top | không |
| lookup | tìm trên web, có `topic` general/news và `timeframe` day/week/month/year | không |
| fetch | đọc nội dung của một URL cụ thể | không |
| format | trình bày các item đã có thành markdown digest | không |
| send | gửi text lên Telegram channel, chỉ gửi khi `confirmed=true` | không |
| policy | tìm trong company policy markdown nội bộ | không |
| papers | tìm paper trên arXiv | không |
| paper_text | tải PDF arXiv và trích text cục bộ | không |
| wikipedia | tra cứu kiến thức nền từ Wikipedia (định nghĩa, lịch sử, tổng quan khái niệm) | **CÓ** |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. "Tin AI hôm nay có gì nổi bật?" — agent sẽ tra web với `topic=news`, `timeframe=day`.
2. "Tóm tắt 5 tweet mới nhất giúp mình" — thiếu handle nên agent **hỏi lại** thay vì đoán bừa; trả lời "Của Elon Musk nhé" để agent gọi `timeline(screenname=elonmusk, limit=5)`.
3. "Cho mình tổng quan trên Wikipedia về cách hoạt động của blockchain" — agent route tới tool `wikipedia` (kiến thức nền, không phải tin tức).
4. "Tổng hợp tin hôm nay rồi đăng lên Telegram cho tôi" — agent **hỏi xác nhận** trước khi gửi, không tự ý đăng.
5. "Giải giúp mình hệ phương trình bậc hai" — ngoài phạm vi research, agent từ chối và không gọi tool nào.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
