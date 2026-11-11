---
noteId: "8c37f7e0dd0111f1a61cc708a9f9c107"
tags: []

---

# Báo cáo cá nhân — Vương Quang Thắng - 2A202603855


## 1. Thông tin thành viên

- Họ tên: Vương Quang Thắng
- MSSV: 2A202603855
- Email: 26ai.thangvq@vinui.edu.vn

## 2. Phần việc phụ trách

Trong nhóm, đảm nhận **Vai trò B (Prompt & Tools Declaration Optimizer)**. Trách nhiệm chính của tôi bao gồm:
- Phân tích chi tiết các file log đánh giá định dạng JSON (`runs/*.json`) sau mỗi lần chạy eval (do A thực hiện) để tìm ra nguyên nhân gốc rễ (root cause) của các cases thất bại.
- Xây dựng giả thuyết tối ưu hóa và trực tiếp chỉnh sửa luật trong `artifacts/system_prompt.md` và `artifacts/tools.yaml`.
- Đảm bảo agent định tuyến (routing) đúng công cụ, truyền đúng tham số (arguments), không bị ảo giác (hallucination) tự đoán thông tin và tuân thủ ranh giới an toàn (không tự ý gửi bài).
- Tích hợp khối khai báo YAML của tool mới (`wikipedia`) vào hệ thống để Vai trò C có thể viết code thực thi.

## 3. Đóng góp cụ thể

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

## 4. Bằng chứng

- **File/commit/PR:** 
  - Các sửa đổi trực tiếp trên file `starter_v0/artifacts/system_prompt.md` (v1).
  - Các sửa đổi trực tiếp trên file `starter_v0/artifacts/tools.yaml` (v2, v3).
  - Khởi tạo nội dung tổng hợp giả thuyết và bằng chứng cho bảng `version_log.csv` và Bảng B1, B2, B6 trong `group_report.md`.

- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng AI (Gemini/ChatGPT) như một đối tác tư vấn (Co-pilot) để hỗ trợ đọc hiểu cấu trúc phức tạp của các file `runs/*.json`, trích xuất lý do fail của từng case một cách nhanh chóng.
  - Nhờ AI phản biện các giả thuyết trước khi đưa vào file YAML để tránh lỗi cú pháp và đảm bảo tính logic.
  - Tự kiểm tra kết quả bằng cách làm việc chặt chẽ với Vai trò A: đợi A chạy xong lệnh `run_eval.py`, nhận lại log mới và so sánh đối chiếu các thông số `metric_before` / `metric_after`.

## 5. Tự đánh giá

- Mức độ hoàn thành: 100% các yêu cầu của Vai trò B.
- Đã nắm vững khái niệm "Evidence-driven loop" (Vòng lặp dựa trên bằng chứng). Tôi hiểu rằng không thể sửa prompt theo cảm tính, mà phải cô lập từng file (`system_prompt` riêng, `tools.yaml` riêng), sửa dựa trên phân tích log cụ thể, và có số liệu cải thiện điểm qua từng vòng (từ 0.70 lên 0.95). 
- Kỹ năng Prompt Engineering được nâng cao rõ rệt, đặc biệt là cách sử dụng "luật cấm" (Negative prompt) và ranh giới hành vi (Boundaries) để kiểm soát model.