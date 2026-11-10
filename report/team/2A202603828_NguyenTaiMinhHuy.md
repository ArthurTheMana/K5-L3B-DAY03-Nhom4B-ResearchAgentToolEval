# Báo cáo cá nhân — NguyenTaiMinhHuy-2A202603828

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tài Minh Huy
- MSSV: 2A202603828
- Email: nguyentaiminhhuy831975@gmail.com

## 2. Phần việc phụ trách
Mình chịu trách nhiệm thiết lập môi trường thực thi, kiểm tra hoạt động của hệ thống, chạy các phiên bản đánh giá khác nhau từ v0 -> v3 và tổng hợp lại các kết quả để báo cáo với nhóm.

Các công việc bao gồm: 
- Thiết lập môi trường (Environment Setup): Cấu hình Python Virtual Environment trên Windows, cài đặt dependencies và kiểm tra môi trường thực thi.

- Kiểm thử ban đầu (Unit Testing): Sử dụng pytest để xác nhận các thành phần có sẵn của hệ thống hoạt động trước khi bắt đầu chỉnh sửa.

- Kiểm tra AI Provider (Provider Preflight): Cấu hình kết nối OpenRouter và xác nhận model openai/gpt-4o-mini có khả năng thực hiện Tool Calling.

- Chạy Baseline Evaluation (v0): Đánh giá Agent ban đầu bằng bộ dữ liệu data/eval_base.json để xác định các lỗi về Tool Routing, Arguments và Safety Boundary.

- Chạy các phiên bản tối ưu (v1, v2, v3): Phối hợp với thành viên B để chạy lại Evaluation sau khi cập nhật System Prompt và Tool Declaration.

- Quản lý phiên bản (Version Management): Ghi nhận kết quả đánh giá, Artifact Version, Prompt Hash, Tools Hash và đường dẫn Run JSON trong artifacts/version_log.csv.

- Kiểm tra tích hợp công cụ mới (Tool Integration): Xác minh Wikipedia Tool của thành viên C đã có các file cần thiết, được đăng ký trong Agent và vượt qua Tool Contract Tests.

- Phối hợp nhóm: Theo dõi tiến độ của thành viên B, C và D, trao đổi kết quả kiểm thử và xác định những lỗi cần tiếp tục xử lý.

...

## 3. Đóng góp cụ thể
### 3.1 Thiết lập môi trường (Environment Setup): Cấu hình Python Virtual Environment trên Windows, cài đặt dependencies và kiểm tra môi trường thực thi.

- Kiểm thử ban đầu (Unit Testing): Sử dụng pytest để xác nhận các thành phần có sẵn của hệ thống hoạt động trước khi bắt đầu chỉnh sửa.

- Kiểm tra AI Provider (Provider Preflight): Cấu hình kết nối OpenRouter và xác nhận model openai/gpt-4o-mini có khả năng thực hiện Tool Calling.

- Chạy Baseline Evaluation (v0): Đánh giá Agent ban đầu bằng bộ dữ liệu data/eval_base.json để xác định các lỗi về Tool Routing, Arguments và Safety Boundary.

- Chạy các phiên bản tối ưu (v1, v2, v3): Phối hợp với thành viên B để chạy lại Evaluation sau khi cập nhật System Prompt và Tool Declaration.

- Quản lý phiên bản (Version Management): Ghi nhận kết quả đánh giá, Artifact Version, Prompt Hash, Tools Hash và đường dẫn Run JSON trong artifacts/version_log.csv.

Kiểm tra tích hợp công cụ mới (Tool Integration): Xác minh Wikipedia Tool của thành viên C đã có các file cần thiết, được đăng ký trong Agent và vượt qua Tool Contract Tests.

Phối hợp nhóm: Theo dõi tiến độ của thành viên B, C và D, trao đổi kết quả kiểm thử và xác định những lỗi cần tiếp tục xử lý.
...

## 4. Bằng chứng

- File/commit/PR:
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

## 5. Tự đánh giá

...
