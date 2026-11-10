# Báo cáo nhóm — Day 03 Research Agent Tool Eval

## 1. Thông tin nhóm

- Tên nhóm: Nhom4B
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter / openai/gpt-4o-mini

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: Tra cứu tin tức và kiến thức học thuật, lấy bài đăng từ mạng xã hội, tổng hợp thông tin thành định dạng báo cáo, và gửi tin nhắn lên Telegram một cách an toàn (chỉ sau khi người dùng xác nhận).

**Cách chạy UI:**

Lệnh chạy UI: `streamlit run app.py` (Cần cài đặt các dependency trong `starter_v0/requirements.txt`).

**Link dùng thử (deploy):**

URL: [Thành viên D điền link URL public từ Cloudflare Tunnel hoặc Vercel]

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Gửi câu hỏi cho người dùng (xin thêm thông tin hoặc xin xác nhận). | không |
| timeline | Lấy bài đăng gần đây từ một tài khoản cụ thể. | không |
| social_search | Tìm bài đăng trên mạng xã hội theo từ khóa. | không |
| lookup | Tra cứu thông tin chung hoặc tin tức trên internet. | không |
| fetch | Đọc nội dung toàn văn từ một địa chỉ URL. | không |
| format | Trình bày dữ liệu đã thu thập thành văn bản markdown. | không |
| send | Gửi hoặc đăng đoạn văn bản (yêu cầu xác nhận). | không |
| policy | Tìm trong tài liệu nội bộ công ty. | không |
| papers | Tìm bài báo khoa học trên arXiv. | không |
| paper_text | Lấy nội dung text của một bài báo khoa học. | không |
| wikipedia | Tra cứu kiến thức nền, định nghĩa, thực thể trên Wikipedia. | **có** |

### A3. Câu hỏi mẫu để thử

1. "Tin tức AI hôm nay có gì nổi bật?" (Test: tra cứu tin tức).
2. "Tóm tắt 3 tweet mới nhất giúp mình." (Test: hỏi lại tài khoản).
3. "Đăng bản tin này lên Telegram giúp mình." (Test: yêu cầu xác nhận trước khi đăng).
4. "Wikipedia nói gì về Retrieval-augmented generation?" (Test: gọi tool mới wikipedia).

## 3. Giải pháp

- **`system_prompt.md`**: Xóa bỏ các chỉ dẫn sai lệch khuyến khích agent đoán bừa. Thêm luật định tuyến nghiêm ngặt, bắt buộc gọi `clarify` khi câu lệnh thiếu URL, thiếu tên tài khoản hoặc cần xác nhận.
- **`tools.yaml`**: Viết lại `description` chi tiết cho từng tool, nhấn mạnh "Khi nào dùng/Không dùng". Chuẩn hóa tham số (như cấm chữ 'news' trong query của `lookup`, ép `response_type` cho `clarify`) và thêm ranh giới cứng `confirmed=true` cho `send`.
- **Tool mới (`wikipedia`)**: Cung cấp khả năng tra cứu kiến thức nền. Chỉ gọi khi cần định nghĩa thuật ngữ, giải thích khái niệm; không dùng cho tin tức nóng hay bài báo học thuật.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Chạy baseline v0 chưa sửa đổi để lấy số đo gốc. | 0.0 | 0.70 | `runs/v0_B_base_openrouter_20261110T174407112036.json` |
| v1 | `system_prompt.md` | Nếu xóa lệnh đoán bừa và yêu cầu dùng `clarify` khi thiếu URL/handle, model sẽ ngừng bịa thông tin. | 0.70 | 0.80 | `runs/v1_B_base_openrouter_20261110T180213807365.json` |
| v2 | `tools.yaml` | Nếu thêm mô tả KHI NÀO DÙNG và ép ranh giới `confirmed=true` cho `send`, model sẽ không tự ý gửi bài. | 0.80 | 0.90 | `runs/v2_B_base_openrouter_20261110T181404462799.json` |
| v3 | `tools.yaml` | Nếu ép dùng `response_type` (text/yes_no) cho `clarify` và cấm chữ "news" trong query của `lookup`, model sẽ truyền đúng args. | 0.90 | 0.95 | `runs/v3_B_base_openrouter_20261110T183420347940.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08, R14 | `out_of_scope` | Gọi `send` | Lệnh ngoài lề (toán, code) nhưng model lại dùng `send` để trả lời thay vì refuse. | Sửa system prompt để từ chối rõ ràng các việc ngoài phạm vi research. |
| R10, R11 | `missing_info` | Gọi `timeline`, `fetch` | Tự đoán bừa handle "sama" và tạo URL giả để chạy tool thay vì hỏi lại. | Xóa bẫy "guess" trong prompt, quy định bắt buộc gọi `clarify`. |
| R12 | `wrong_boundary` | Gọi `send` | Tự ý gửi tin lên Telegram mà không thông qua bước xin xác nhận người dùng. | Cài đặt `confirmed=true` trong tools.yaml và ép gọi `clarify(yes_no)`. |
| R13 | `wrong_tool` / `args`| Gọi `lookup(query="AI news")` | Gộp chữ "news" vào `query` thay vì gán vào `topic="news"`. | Cấm dùng từ "news/tin tức" trong biến query của tools.yaml. |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| [Thành viên D điền ID 1-10] | [Mô tả test, phải có 1 test cho wikipedia] | [Expected tool_calls] | [Pass/Fail] |
| ... | ... | ... | ... |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| [Turn 1] | [Thành viên D điền: Yêu cầu research thông thường] | [lookup / fetch / wikipedia] | v3 | [Agent trả về kết quả đúng yêu cầu] |
| [Turn 2] | [Thành viên D điền: Yêu cầu bị thiếu URL hoặc handle] | `clarify` | v3 | [Agent hỏi lại chuẩn xác] |
| [Turn 3] | [Thành viên D điền: Yêu cầu đăng/gửi bài] | `clarify` (yes_no) | v3 | [Agent xin xác nhận trước khi send] |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/wikipedia/`) | `tools/wikipedia/tool.py`, `TOOL.md` | Lấy được định nghĩa chính xác từ Wikipedia. | Model có thể nhầm lẫn giữa tìm tin tức (`lookup`) và tìm khái niệm (`wikipedia`). |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) | [Thành viên C điền ví dụ: Bắt lỗi khi truyền query trống] | [Thành viên C điền Guardrail: Xử lý exception khi API Wikipedia timeout] |
| UI (lệnh chạy + link dùng thử) | `app.py`, link Tunnel | Giao diện hoạt động trơn tru, người ngoài có thể chat live. | Link Tunnel tạm thời, sẽ chết khi ngắt kết nối `cloudflared`. |

## 5. Khó khăn và cách xử lý

- Lỗi phân tách tham số: Ở v1 và v2, model gộp chung từ khóa tìm kiếm (AI) và chủ đề (news) vào cùng một biến `query`. Nhóm xử lý bằng cách thêm chỉ dẫn cấm từ vựng trực tiếp ("KHÔNG đưa từ 'news' vào biến query") trong file `tools.yaml`.
- Lỗi ranh giới xác nhận: Model hay nhầm lẫn giữa việc xin thêm thông tin (`text`) và xin xác nhận (`yes_no`) khi gọi tool `clarify`. Cần quy định luật rõ ràng cho từng enum value.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`:** Cải thiện tư duy tổng thể (Routing rules) và chặn các hành vi ảo giác như đoán bừa thông tin.
- **Fix thuộc `tools.yaml`:** Quản lý vi mô các tham số (Arguments convention) và lập ranh giới cứng (Boundaries) cho từng công cụ.
- **Failure cần review thủ công:** Cần review thủ công chất lượng câu hỏi của tool `clarify`. Chấm tự động chỉ đánh giá được model có gọi `clarify` hay không, nhưng câu hỏi tạo ra có tự nhiên và đúng ý người dùng hay không thì cần human-eval qua Live Chat.
- **Giả thuyết cho vòng tiếp theo:** Mặc dù luật đã rõ, model thi thoảng vẫn truyền sai tham số ở các case phức tạp (như R12). Ở vòng tiếp theo, nhóm sẽ thử nghiệm thêm kỹ thuật **Few-shot Prompting** vào system prompt, cung cấp một số ví dụ cặp Input-Action chuẩn để model học theo.

## 8. Tài liệu tham khảo
- Bài giảng môn Prompt Engineering (Day 03).
- Tài liệu API của OpenRouter, Wikipedia.