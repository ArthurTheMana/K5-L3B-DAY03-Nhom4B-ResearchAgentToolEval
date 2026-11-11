# Team

## Thông tin nhóm

- Tên nhóm: Nhom4B
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Nhom4B-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
  - URL repo: https://github.com/ArthurTheMana/K5-L3B-DAY03-Nhom4B-ResearchAgentToolEval
  - Nhánh nộp: `main`
  - Commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Vương Quang Thắng | 2A202603855 | vuongquangthang0311@gmail.com | vuongquangthang | Prompt & tool declaration — sửa `system_prompt.md` + `tools.yaml` qua v1→v3 |
|   2 | Nguyễn Tài minh Huy | 2A202603828 | nguyentaiminhhuy831975@gmail.com | ArthurTheMana | Nhóm trưởng — setup, chạy v0–v3, `version_log.csv`, gom bài |
|   3 | Trần Thị Nhài | 2A202603911 | nhainhinhanh6a@gmail.com | `chanhochust` | Tool mới + unit test — `wikipedia` |
|   4 | Vũ Văn Trường | 2A202603910 | tini.vu.0@gmail.com | `Sz3RO` | Eval nhóm + UI + demo — 10 eval case của nhóm, UI Streamlit (`app.py`) có streaming token thật, transcript live chat, Phần A + poster |


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
Trần Thị Nhài : [2A202603911_TranThiNhai.md](report/team/2A202603911_TranThiNhai.md)

## Trần Thị Nhài — 2A202603911

### Phần việc phụ trách

- **Tool mới + unit test (CP3):** tool `wikipedia` (tra cứu kiến thức nền), đăng ký registry, unit test, bằng chứng pytest.

### Đóng góp cụ thể

- Tool `starter_v0/tools/wikipedia/` (`tool.py` + `TOOL.md`): gọi Wikipedia REST API, không cần API key, gửi `User-Agent` riêng, kiểm tra input xấu từ model, trả error dict thay vì raise; output cùng shape `items` với `lookup`/`fetch`.
- Đăng ký `"wikipedia": wiki_search` trong `starter_v0/tools/__init__.py`; soạn khối khai báo `tools.yaml` gửi bạn Vương Quang Thắng và gợi ý eval case route tới tool cho bạn Vũ Văn Trường.
- 10 hàm test / 23 trường hợp trong `starter_v0/tests/test_tools_todo.py` (happy path, input xấu từ model, nhánh lỗi HTTP/timeout), tất cả pass, chạy offline.
- Điền phần tool mới và unit test trong `report/team/group_report.md` (B5a).

### Bằng chứng

- Commit: `33fa5c7` (add new tool), `272953a` (pytest output), `a316eac` (báo cáo cá nhân), `58e2083` (fill B5a).
- Số liệu: 23 test `wikipedia` passed · contract test `wikipedia` 5/5 · toàn suite `pytest` 90 passed / 0 failed · base v3 0 case gọi nhầm `wikipedia` · group v3 3/3 case route tới `wikipedia` PASS.
- Công cụ AI: Claude Code hỗ trợ viết khung code/test, soạn khai báo YAML, giúp sửa lỗi SSL và chạy các lệnh kiểm tra; tôi xem output và đối chiếu số liệu với run JSON trước khi đưa vào báo cáo. Chi tiết ở báo cáo cá nhân.


## Nguyễn Tài Minh Huy - 2A202603828

### Phần việc phụ trách

- **Nhóm trưởng (CP1, CP2, CP4):** Setup môi trường, chạy Base và Group Evaluation, phân tích lỗi, quản lý `version_log.csv`, phối hợp và tổng hợp kết quả nhóm.

### Đóng góp cụ thể

- Thiết lập Python 3.14.3, môi trường `.venv`, cài đặt dependencies; xử lý lỗi PowerShell và OpenRouter API Key; chạy preflight thành công với `openai/gpt-4o-mini`.
- Chạy Base Evaluation v0–v3, ghi nhận Case Accuracy tăng từ **70% (14/20)** lên **100% (20/20)** sau khi nhóm tối ưu System Prompt và Tool Declaration.
- Phân tích các case FAIL (`R03`, `R10`, `R11`, `R12`, `R13`), phản hồi cho Quang Thắng để cải thiện Tool Routing, Arguments và quy tắc xác nhận.
- Chạy Group Evaluation với `data/eval_group.json`: **10/10 PASS**, Tool Routing và Argument Accuracy đều đạt 100%, Provider Errors = 0.
- Cập nhật `artifacts/version_log.csv`, lưu Run JSON, Prompt Hash, Tools Hash và kiểm tra tích hợp Wikipedia Tool; Tool Contract Tests đạt **60 PASS**.
- Phối hợp các thành viên, kiểm tra bằng chứng Evaluation và hoàn thiện báo cáo cá nhân.

### Bằng chứng

- **Commit:** `ba5b553` (Version Log), `a37adcb` (Base và Group Evaluation v3), `5aa3ab7` và `d7936b8` (báo cáo cá nhân).
- **Kết quả:** Base v0 **14/20 PASS**; Base v3 **20/20 PASS**; Group v3 **10/10 PASS**; Tool Contract **60 PASS**.
- **File:** `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/`, `report/team/2A202603828_NguyenTaiMinhHuy.md`.
- **Công cụ AI:** ChatGPT hỗ trợ phân tích yêu cầu, xử lý lỗi môi trường, giải thích Evaluation và tổng hợp báo cáo. Mình trực tiếp chạy lệnh, kiểm tra Terminal Output và đối chiếu Run JSON.



## Vương Quang Thắng - 2A202603855

## Phần việc phụ trách

Trong nhóm, đảm **Vai trò B (Prompt & Tools Declaration Optimizer)**. Trách nhiệm chính bao gồm:
- Phân tích chi tiết các file log đánh giá định dạng JSON (`runs/*.json`) sau mỗi lần chạy eval (do A thực hiện) để tìm ra nguyên nhân gốc rễ (root cause) của các cases thất bại.
- Xây dựng giả thuyết tối ưu hóa và trực tiếp chỉnh sửa luật trong `artifacts/system_prompt.md` và `artifacts/tools.yaml`.
- Đảm bảo agent định tuyến (routing) đúng công cụ, truyền đúng tham số (arguments), không bị ảo giác (hallucination) tự đoán thông tin và tuân thủ ranh giới an toàn (không tự ý gửi bài).
- Tích hợp khối khai báo YAML của tool mới (`wikipedia`) vào hệ thống để Vai trò C có thể viết code thực thi.

## Đóng góp cụ thể

Đã thực hiện chuỗi vòng lặp tối ưu hóa dựa trên bằng chứng qua 3 phiên bản:

**Vòng 1 (Tối ưu `system_prompt.md`):**
- *Phát hiện:* Dựa trên log v0, tôi nhận thấy model mắc lỗi `missing_info` do tự đoán bừa tên tài khoản (R10, R11) và lỗi `out_of_scope` do gọi tool vô tội vạ cho câu hỏi toán học/lập trình (R08, R14). Nguyên nhân là do các "bẫy" hướng dẫn ngầm trong prompt gốc.
- *Hành động:* Xóa các chỉ dẫn độc hại ("make a sensible guess"). Bổ sung các chỉ dẫn định tuyến mạnh: bắt buộc gọi `clarify` khi thiếu URL/handle và từ chối các yêu cầu nằm ngoài phạm vi research.
- *Kết quả:* Điểm `case_accuracy` tăng từ 0.70 lên 0.80.

**Vòng 2 (Tối ưu `tools.yaml`):**
- *Phát hiện:* Dù định tuyến đúng, model mắc lỗi `wrong_boundary` ở R12 (tự gửi bài lên Telegram). 
- *Hành động:* Tôi viết lại mô tả của tool `send`, nhấn mạnh luật KHÔNG BAO GIỜ được gọi nếu người dùng chưa phê duyệt và ép bắt buộc phải có biến `confirmed=true`. Đồng thời, chuẩn hóa lại mô tả "KHI NÀO DÙNG/KHÔNG DÙNG" cho toàn bộ các tool còn lại.
- *Kết quả:* `case_accuracy` tăng lên 0.90, `tool_routing_accuracy` đạt 1.0 (Hoàn hảo).

**Vòng 3 (Chuẩn hóa Arguments & Thêm Tool):**
- *Phát hiện:* Log v2 chỉ ra lỗi tinh vi về tham số: model gộp chữ "news" vào biến `query` (R13) và bỏ quên biến `response_type` khi gọi tool `clarify` (R11, R12).
- *Hành động:* Tôi thêm luật cấm trực tiếp "KHÔNG đưa các từ 'news' hoặc 'tin tức' vào biến query" cho tool `lookup`. Đồng thời, ép cứng luật phải dùng `response_type='yes_no'` khi xin xác nhận và `'text'` khi hỏi thêm thông tin. Cuối cùng, tôi tích hợp khai báo YAML cho tool `wikipedia` từ Vai trò C.
- *Kết quả:* Sửa thành công lỗi tham số, `case_accuracy` đạt 0.95.

## Bằng chứng

- **File/commit/PR:** 
  - Các sửa đổi trực tiếp trên file `starter_v0/artifacts/system_prompt.md` (v1).
  - Các sửa đổi trực tiếp trên file `starter_v0/artifacts/tools.yaml` (v2, v3).
  - Khởi tạo nội dung tổng hợp giả thuyết và bằng chứng cho bảng `version_log.csv` và Bảng B1, B2, B6 trong `group_report.md`.

- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng AI (Gemini/ChatGPT) như một đối tác tư vấn (Co-pilot) để hỗ trợ đọc hiểu cấu trúc phức tạp của các file `runs/*.json`, trích xuất lý do fail của từng case một cách nhanh chóng.
  - Nhờ AI phản biện các giả thuyết trước khi đưa vào file YAML để tránh lỗi cú pháp và đảm bảo tính logic.
  - Tự kiểm tra kết quả bằng cách làm việc chặt chẽ với Vai trò A: đợi A chạy xong lệnh `run_eval.py`, nhận lại log mới và so sánh đối chiếu các thông số `metric_before` / `metric_after`.
