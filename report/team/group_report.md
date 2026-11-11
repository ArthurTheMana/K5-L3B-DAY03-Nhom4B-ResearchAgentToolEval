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

URL: [https://nhom4b-research-agent.streamlit.app/](https://nhom4b-research-agent.streamlit.app/)


**Public UI Demo:**

- **Platform:** Streamlit Community Cloud
- **Provider:** OpenRouter
- **Version:** v3
- **Deployment:** Public
- **Main file:** `starter_v0/app.py`

**Live Demo Verification:**

Mình đã kiểm tra ứng dụng Research Agent sau khi deploy trên Streamlit Community Cloud. Giao diện hoạt động và Agent đã chọn Wikipedia Tool để xử lý câu hỏi về Alan Turing, sau đó trả lời bằng tiếng Việt.

**Test Question:**

Tra cứu Wikipedia và cho mình biết Alan Turing là ai. Tóm tắt trong 3 câu bằng tiếng Việt.

**Result:** Agent gọi `wikipedia` và trả về câu trả lời phù hợp.

[[]](Streamlit_Testing.png)

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
| v3 | `tools.yaml` | Cập nhật quy tắc `clarify.response_type` và kiểm tra lại cách truyền Arguments sau khi nhóm sửa Tool Declaration. | 0.90 | 1.00 | `runs/v3_B_base_openrouter_20261111T002233736709.json` |

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
| G01_wikipedia_background_fact | Kiến thức nền (tổng quan khái niệm) → `wikipedia`, không dùng `lookup`/`papers` | `wikipedia` | **PASS** — gọi `wikipedia` |
| G02_wikipedia_vs_lookup_news | Sự kiện có thời điểm → `lookup(topic=news, timeframe=day)`, **không** dùng `wikipedia` | `lookup` | **PASS** — gọi `lookup(topic=news, timeframe=day)` |
| G03_missing_wikipedia_topic | Thiếu đối tượng tra cứu → phải `clarify`, không tự đoán | `clarify(response_type=text)` | **PASS** — gọi `clarify` |
| G04_greeting_no_tool | Lời cảm ơn → trả lời thẳng, không gọi tool nào (kể cả `send`) | `no_tool` | **PASS** — không gọi tool nào |
| G05_out_of_scope_creative_writing | Yêu cầu sáng tác văn học ngoài phạm vi research | `no_tool` (refuse) | **PASS** — không gọi tool nào |
| G06_switch_wikipedia_to_web_news | 3 lượt: đổi nguồn wikipedia→web, khóa `timeframe=day`, `topic=news` | `lookup` | **PASS** — gọi `lookup(topic=news, timeframe=day)` |
| G07_missing_url_then_fetch | 3 lượt: thiếu URL → lượt 2 cấp URL → chỉ đọc link đó | `fetch(url=…)` | **PASS** — gọi `fetch(url=…)` đúng link |
| G08_wikipedia_carryover_query | 3 lượt: giữ tool wikipedia, đổi query, yêu cầu bản tiếng Việt | `wikipedia(query="học máy", lang="vi")` | **PASS** — gọi `wikipedia(query="học máy", lang="vi")` |
| G09_confirmed_send_boundary | 3 lượt: user đã xác nhận rõ → agent phải hành động `confirmed=true`, không hỏi lại | `send(confirmed=true)` | **PASS** — gọi `send(confirmed=true)` |
| G10_wikipedia_plus_news_parallel | 3 lượt: cần cả kiến thức nền lẫn tin mới → gọi **cả hai** tool | `wikipedia` + `lookup(topic=news)` | **PASS** — gọi cả `wikipedia` **và** `lookup(topic=news)` |

**Kết quả run:** `case_accuracy = 1.00` (10/10 PASS), `tool_routing_accuracy = 1.00`, `argument_accuracy = 1.00`, `multiturn_accuracy = 1.00`, `provider_error_cases = 0`, `measured_cases = 10/10` — run hợp lệ theo quy tắc chấm.

- Run file: `starter_v0/runs/v3_B_group_openrouter_20261111T002352968732.json` (chạy lại 00:23 sau khi `tools.yaml` được sửa — chạy đầu lúc 18:48 bị G09 fail do mô tả `clarify` cũ, đã phân tích ở báo cáo cá nhân vai trò D)
- Provider/model: `openrouter` / `openai/gpt-4o-mini` (cùng model với v0–v3)
- Artifact version: `v3+pac40825b391a+tca4674f23b12` (khớp dòng v3 trong `version_log.csv` và artifacts hiện tại trong repo)
- Lệnh tái lập: `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json`

Bộ 10 case phủ đủ 6 loại lỗi của `allowed_failure_types` và có **3 case route tới tool mới `wikipedia`** (G01, G08, G10).

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| [Turn 1] | "Cho mình tổng quan trên Wikipedia về blockchain" | `wikipedia(query="Blockchain", lang="en")` | v3 (`artifact_version = v3+p8b1d8369242a+tff4501744c70`) | Agent trả về 3 mục từ Wikipedia kèm link thật (`Blockchain`, `Cryptocurrency`, `Fork (blockchain)`) |
| [Turn 2] | "Tóm tắt 5 tweet mới nhất giúp mình" | *(không gọi tool)* | v3 | Agent **hỏi lại** vì thiếu tên tài khoản: *"Bạn vui lòng cung cấp tên tài khoản Twitter…"*, không đoán bừa |
| [Turn 3] | "Của Elon Musk nhé" | `timeline(screenname="elonmusk", limit=5)` | v3 | Agent dùng đúng handle và giữ `limit=5` từ lượt trước; tool báo lỗi vì thiếu `RAPIDAPI_KEY` và agent **báo lỗi thật, không bịa kết quả** |
| [Turn 4] | "Đăng bản tin đó lên Telegram cho tôi" | `clarify(response_type="yes_no")` | v3 | Agent **xin xác nhận trước khi gửi**: *"Bạn có thể xác nhận nội dung bản tin…?"*, chưa gọi `send` |

**Transcript chính:** `starter_v0/transcripts/v3_openrouter_20261110T185012964883.transcript.json` — 4 lượt, provider `openrouter`, model `openai/gpt-4o-mini`.

**Transcript sinh từ UI Streamlit (chạy lại sau khi `tools.yaml` được sửa, artifact khớp repo hiện tại `v3+pac40825b391a+tca4674f23b12`):** `starter_v0/transcripts/v3_openrouter_20261111T005307903185.transcript.json` — 3 lượt, phủ đủ 3 hành vi rubric: yêu cầu thường → `wikipedia` trả dữ liệu thật · thiếu thông tin → agent hỏi lại · yêu cầu đăng → `clarify` (`status: waiting_for_user`).

Hai transcript bổ sung (cùng version v3):
- `v3_openrouter_20261110T184912065678.transcript.json` — 4 lượt: wikipedia → hỏi lại → timeline → lookup.
- `v3_openrouter_20261110T184936514496.transcript.json` — 1 lượt: yêu cầu đăng Telegram → `clarify(response_type="yes_no")`.

Cả 3 transcript sinh bằng `python chat.py --provider openrouter --version v3` và đã commit vào repo.

> ⚠️ Một hạn chế quan sát được: ở lượt 2 agent hỏi lại bằng **text** chứ không gọi tool `clarify`, vì `chat.py` không ép `tool_choice`; còn `run_eval.py` thì ép `tool_choice="required"` cho các case cần gọi tool. Đây là khác biệt giữa *hành vi thật khi chat* và *hành vi được chấm tự động* — eval không đo được lỗi "hỏi lại nhưng không dùng tool", nên cần đọc transcript thủ công.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/wikipedia/`) | `tools/wikipedia/tool.py`, `TOOL.md` | Lấy được định nghĩa chính xác từ Wikipedia. Model route đúng: group v3 **3/3 case `wikipedia` PASS** (G01, G08, G10) | Model có thể nhầm lẫn giữa tìm tin tức (`lookup`) và tìm khái niệm (`wikipedia`). Đã kiểm chứng: base v3 (bản đầu tiên có `wikipedia`) **0 case gọi nhầm**, R08/R09/R14 (không được gọi tool) đều PASS |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (mục `wikipedia`); output: `starter_v0/analysis/pytest_wikipedia.txt` — **23 passed** (10 hàm test, có parametrize), contract test `wikipedia` 5/5, toàn suite **90 passed, 0 failed** | Phủ đủ 3 nhóm: **happy path** (request đúng URL/params/`User-Agent`, map response thành `items`, `lang="vi"` gọi `vi.wikipedia.org`); **input xấu từ model** (query rỗng/`None`/số → trả error dict và **không gửi request**; `lang` ngoài enum → `en`; `limit="5"`/`50`/`-3` được ép kiểu và kẹp 1–10); **nhánh lỗi** (HTTP 403/429/500, timeout → error dict, payload lạ → `items: []`) | Tool **không bao giờ raise**: mọi lỗi đều trả error dict để agent không crash. Test chạy **offline** (mock mạng bằng `fake_http`, không tốn credit). Mỗi test assert cả request gửi đi lẫn kết quả trả về |
| UI (lệnh chạy + link dùng thử) | `app.py`, link Tunnel | Giao diện hoạt động trơn tru, người ngoài có thể chat live. | Link Tunnel tạm thời, sẽ chết khi ngắt kết nối `cloudflared`. |

Tool unit tests: tool `wikipedia` có **10 hàm test / 23 trường hợp**, tất cả pass. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: Wikipedia trả **HTTP 403** cho User-Agent mặc định của thư viện (`python-requests/2.34.2`) và **200** khi gửi User-Agent riêng của tool (đã kiểm tra thực tế). Nếu code quên gửi header này, model vẫn gọi đúng `wikipedia(query=...)` nên eval báo **PASS** (eval chỉ chấm tên tool + args), nhưng mọi lần gọi thật đều lỗi. Test `test_wikipedia_sends_query_with_user_agent_and_maps_pages` assert header `User-Agent` nên bắt được lỗi này ngay, offline.

## 5. Khó khăn và cách xử lý

- Lỗi phân tách tham số: Ở v1 và v2, model gộp chung từ khóa tìm kiếm (AI) và chủ đề (news) vào cùng một biến `query`. Nhóm xử lý bằng cách thêm chỉ dẫn cấm từ vựng trực tiếp ("KHÔNG đưa từ 'news' vào biến query") trong file `tools.yaml`.
- Lỗi ranh giới xác nhận: Model hay nhầm lẫn giữa việc xin thêm thông tin (`text`) và xin xác nhận (`yes_no`) khi gọi tool `clarify`. Cần quy định luật rõ ràng cho từng enum value.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

| Vai trò | Phần việc | File sở hữu chính |
|---|---|---|
| A — Nhóm trưởng | Setup, chạy v0–v3, `version_log.csv`, bảng B1/B2, gom bài | `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/` |
| B — Prompt & tool declaration | Sửa `system_prompt.md` + `tools.yaml` qua 3 vòng, đặt giả thuyết mỗi version | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml` |
| C — Tool mới + unit test | Viết `wikipedia`, đăng ký registry, 23 unit test (10 hàm test) | `starter_v0/tools/wikipedia/`, `starter_v0/tests/test_tools_todo.py` |
| D — Eval nhóm + UI + demo | 10 eval case, UI Streamlit (`app.py`) có streaming token thật, transcript, Phần A | `starter_v0/data/eval_group.json`, `starter_v0/app.py`, `starter_v0/streaming.py`, `starter_v0/transcripts/`, `report/team/` |

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`:** Cải thiện tư duy tổng thể (Routing rules) và chặn các hành vi ảo giác như đoán bừa thông tin.
- **Fix thuộc `tools.yaml`:** Quản lý vi mô các tham số (Arguments convention) và lập ranh giới cứng (Boundaries) cho từng công cụ.
- **Failure cần review thủ công:** Cần review thủ công chất lượng câu hỏi của tool `clarify`. Chấm tự động chỉ đánh giá được model có gọi `clarify` hay không, nhưng câu hỏi tạo ra có tự nhiên và đúng ý người dùng hay không thì cần human-eval qua Live Chat.
- **Giả thuyết cho vòng tiếp theo:** Mặc dù luật đã rõ, model thi thoảng vẫn truyền sai tham số ở các case phức tạp (như R12). Ở vòng tiếp theo, nhóm sẽ thử nghiệm thêm kỹ thuật **Few-shot Prompting** vào system prompt, cung cấp một số ví dụ cặp Input-Action chuẩn để model học theo.

## 8. Tài liệu tham khảo
- Bài giảng môn Prompt Engineering (Day 03).
- Tài liệu API của OpenRouter, Wikipedia.
- **Streamlit** — https://streamlit.io (Apache-2.0) — UI của nhóm (`app.py`, gồm `st.chat_message`, `st.write_stream` cho streaming).
- **Wikipedia REST API** — https://en.wikipedia.org/w/rest.php/v1/search/page (nguồn dữ liệu cho tool `wikipedia` của nhóm).
- **Cloudflare Tunnel** — https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/ (đưa UI local ra link public cho team khác thử).
- Tài liệu của lab: [README.md](../../README.md) · [RUBRIC.md](../../RUBRIC.md) · [CHECKPOINTS.md](../../CHECKPOINTS.md) · [docs/TOOL-SETUP.md](../../docs/TOOL-SETUP.md)
