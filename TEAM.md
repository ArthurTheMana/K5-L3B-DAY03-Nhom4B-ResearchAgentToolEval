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
|   2 | Nguyễn Tài minh Huy | 2A202603828 |        |        | Nhóm trưởng — setup, chạy v0–v3, `version_log.csv`, gom bài |
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

-
