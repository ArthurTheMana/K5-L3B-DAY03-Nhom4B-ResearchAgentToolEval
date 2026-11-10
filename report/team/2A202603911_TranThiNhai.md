# Báo cáo cá nhân — Trần Thị Nhài

## 1. Thông tin thành viên

- Họ tên: Trần Thị Nhài
- MSSV: 2A202603911
- Email: nhainhinhanh6a@gmail.com
- GitHub: chanhochust
- Vai trò trong nhóm: Viết Tool mới + unit test (CP3)

## 2. Phần việc phụ trách

Tôi phụ trách **CP3**: thêm một tool mới cho research agent và chứng minh code của tool chạy đúng bằng unit test.

1. **Tool mới `wikipedia`**: tra cứu kiến thức nền (định nghĩa, khái niệm, người, tổ chức, lịch sử) qua Wikipedia REST API.
2. **Đăng ký và khai báo tool**: đăng ký trong registry `tools/__init__.py`, soạn khối khai báo cho `artifacts/tools.yaml` để B (người giữ file) đưa vào.
3. **Unit test cho tool**: ít nhất 3 nhóm test theo rubric (happy path, input xấu từ model, nhánh lỗi), `pytest` 0 failed.
4. **Phối hợp với nhóm**: gợi ý eval case route tới tool cho D, kiểm tra tool mới không làm giảm điểm base eval.

## 3. Đóng góp cụ thể

### 3.1 Chọn tool

Tôi chọn `wikipedia` theo 3 tiêu chí:

- **Có chỗ đứng riêng**, không trùng các tool có sẵn: tin mới → `lookup`, URL cụ thể → `fetch`, paper → `papers`, còn câu hỏi "X là gì" → `wikipedia`. Nhờ vậy model có ranh giới rõ để chọn.
- **Không cần API key**, nên không tốn quota và cả nhóm chạy được ngay.
- **Dễ mock khi test**: một request GET, response JSON đơn giản.

### 3.2 Code tool — `starter_v0/tools/wikipedia/tool.py` + `TOOL.md`

| Quyết định | Lý do |
|---|---|
| Gọi `requests.get` (thuộc tính của module) | Để fixture `fake_http` trong `conftest.py` mock được |
| Gửi header `User-Agent` riêng | Wikipedia trả **403** với UA mặc định `python-requests/2.34.2`, trả **200** với UA của tool. Tôi đã tự kiểm tra thực tế cả hai trường hợp |
| Kiểm tra input xấu từ model | Query rỗng/`None`/số/list → error dict, **không gửi request**; `lang` ngoài `{en, vi}` → `en`; `limit` dạng chuỗi được ép kiểu và kẹp 1–10 |
| Không bao giờ raise | Toàn bộ nằm trong `try/except`, lỗi HTTP/timeout trả error dict qua `err()` của `_shared.py`, giống các tool có sẵn |
| Output `items[{title, url, source, summary}]` | Cùng shape với `lookup`/`fetch`, nên kết quả đưa thẳng vào `format` được |

Kiểm tra với API thật: query `"Retrieval-augmented generation"` trả đúng bài ở vị trí 1; query tiếng Việt `"Trí tuệ nhân tạo"` với `lang="vi"` trả đúng bài trên `vi.wikipedia.org`.

### 3.3 Khai báo tool trong `tools.yaml`

Tôi soạn khối khai báo và gửi B. Hai điểm tôi thêm dựa trên quan sát thật:

- **Query phải là tên đầy đủ, không viết tắt.** Khi thử, `wikipedia("RAG")` trả bài *Rag* (miếng giẻ), còn `"Retrieval-augmented generation"` trả đúng bài. Đây là lỗi model truyền args, không phải lỗi code, nên tôi sửa ở description.
- **Không gọi tool cho toán/code.** Base eval có case R08 (*"nguyên hàm của x^2 là gì?"*) và R14 (viết code) kỳ vọng không gọi tool. Một tool cho câu "X là gì" rất dễ bị gọi nhầm cho các câu này, nên description ghi rõ "KHÔNG gọi tool nào, kể cả wikipedia".

### 3.4 Unit test — `starter_v0/tests/test_tools_todo.py`

10 hàm test, chạy thành **23 trường hợp** (dùng `parametrize`), tất cả pass, chạy offline:

| Nhóm | Test kiểm tra |
|---|---|
| Happy path | Request đúng URL, params, có `User-Agent`; map response đúng; bỏ trang thiếu `key`; fallback `excerpt` đã xóa thẻ HTML; `lang="vi"` gọi `vi.wikipedia.org`; không trả quá `limit` |
| Input xấu từ model | Query `""`, `"   "`, `None`, `123`, list → error, không request; `lang` `"fr"`/`""`/`None`/`1` → `en`; `limit` `"5"`→5, `50`→10, `-3`→1, `0`→3, `None`→3; `limit="abc"` → error |
| Nhánh lỗi | HTTP 403/429/500 → error dict `HTTPError`; timeout → error dict `Timeout`; payload lạ → `items: []` |

Mỗi test assert cả **request gửi đi** lẫn **kết quả trả về**.

**Ví dụ lỗi unit test bắt được mà eval không bắt được:** nếu tool quên gửi `User-Agent` riêng, model vẫn gọi đúng `wikipedia(query=...)` nên eval báo PASS (eval chỉ chấm tên tool + args), nhưng mọi lần gọi thật đều bị 403. Test `test_wikipedia_sends_query_with_user_agent_and_maps_pages` bắt được lỗi này.

### 3.5 Kiểm chứng trên run thật của nhóm

- **Base v3** (bản đầu tiên có `wikipedia`, `tools_hash=ff4501744c70`): `case_accuracy = 0.95`, **0 case gọi nhầm `wikipedia`**; R08/R09/R14 (không được gọi tool) đều PASS.
- **Group v3**: 10/10 PASS, trong đó **3/3 case route tới `wikipedia`** đều PASS (G01; G08 với `lang="vi"`; G10 gọi song song với `lookup`).

### 3.6 Phối hợp và báo cáo

- Thống nhất thứ tự: code tool lên `main` trước, khai báo YAML sau, để contract test không đỏ.
- Gửi D 4 eval case gợi ý (route tới `wikipedia`, `lang="vi"`, case kiểm tra ngược "tin hôm nay → `lookup`", multi-turn đổi ý). Tôi lưu ý D không kiểm tra giá trị `query`, vì bộ chấm so sánh chính xác chuỗi.
- Điền phần tool mới trong báo cáo nhóm (mục 3.3, B5a, mục 6) và `TEAM.md`; sửa các chỗ ghi sai số test ("3 test" → 23) và sai người làm phần C.

## 4. Bằng chứng

- **Commit:** `33fa5c7` (add new tool: tool + registry + test), `272953a` (pytest output).
- **File:** `starter_v0/tools/wikipedia/tool.py`, `starter_v0/tools/wikipedia/TOOL.md`, `starter_v0/tools/__init__.py`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/analysis/pytest_wikipedia.txt`.
- **pytest:** 23 test `wikipedia` passed; contract test `wikipedia` 5/5 passed; toàn suite 90 passed, 0 failed, 14 skipped (skip là stub của tool có sẵn).
- **Run:** `starter_v0/runs/v3_B_base_openrouter_20261110T183420347940.json`, `starter_v0/runs/v3_B_group_openrouter_20261110T184843874713.json`.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng **Claude Code** (trợ lý AI trong VS Code) để: đọc và tóm tắt đề lab, đề xuất cách chia việc, viết khung code tool và unit test, soạn khối YAML và eval case gợi ý, chẩn đoán lỗi SSL, sửa nháp báo cáo.
  - Cách tự kiểm tra:
    - chạy `pytest` sau mỗi thay đổi và trên `main` mới nhất sau mỗi lần pull;
    - gọi API Wikipedia thật để xác nhận tool trả đúng dữ liệu;
    - tự gọi Wikipedia với UA mặc định và UA của tool để kiểm chứng câu "403 nếu thiếu User-Agent". Kết quả cho thấy câu chữ ban đầu chưa chính xác (403 là với UA mặc định của `requests`, không phải do thiếu header), và tôi đã sửa lại;
    - đọc run JSON v3 (base và group) để kiểm chứng tool không bị gọi nhầm và được route đúng;
    - thử trước kết quả merge với `main` mới nhất trước khi push.

## 5. Tự đánh giá

**Đã làm được:**

- Hoàn thành phần bắt buộc của CP3 (rubric C4): tool mới đủ `tool.py`, `TOOL.md`, đăng ký registry và `tools.yaml`; 23 unit test phủ đủ 3 nhóm; `pytest` 0 failed.
- Tool được model dùng đúng trên run thật (3/3 case group PASS) và không làm giảm base eval (0 lần gọi nhầm).
- Mọi số liệu trong báo cáo đều trỏ được tới file, run hoặc commit cụ thể.

**Khó khăn và cách xử lý:**

- **Avast HTTPS scanning** chặn kết nối SSL từ Python (`CERTIFICATE_VERIFY_FAILED`) cho mọi API. Tôi tìm ra nguyên nhân (PowerShell gọi được, Python thì không), rồi tắt HTTPS scanning trong Avast Web Shield.

**Phát hiện thêm (chưa xử lý, để làm bonus):**

- Tool có sẵn `send` có bug: `send(text, confirmed="false")` (chuỗi thay vì boolean) **vẫn gửi thật**, vì chuỗi `"false"` là truthy. Dự định: viết regression test trước, sau đó sửa thành `if confirmed is not True`.

**Cần cải thiện:**

- Cải thiện tool: Tool chỉ trả tóm tắt ngắn, không trả nội dung bài. summary chỉ là description hoặc excerpt (một dòng). Muốn trả lời sâu hơn thì agent phải fetch thêm URL. Bằng chứng: tool.py, trường summary.
- Phần bonus (regression test cho `send`, điền 14 stub còn lại, viết thêm tool) chưa làm.
