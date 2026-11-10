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

### 3.1 `artifacts/system_prompt.md` (v1)

Starter v0 cố ý dạy agent hành xử sai: *"đoán thay vì hỏi"*, *"gửi thì cứ gửi"*, *"luôn làm trong một bước"*, *"chọn một tool và đoán args"*. v1 thay toàn bộ bằng:

- **Routing rules** rõ ràng cho `timeline` / `social_search` / `lookup` / `fetch` / `clarify`.
- **Bắt buộc `clarify`** khi request mơ hồ, thiếu URL cụ thể hoặc thiếu tên tài khoản — không được đoán bừa.
- Cho phép **nhiều bước**, gọi tool tuần tự khi cần.

Kết quả: `tool_routing_accuracy` 0.75 → **1.00**, `case_accuracy` 0.70 → 0.80.

### 3.2 `artifacts/tools.yaml` (v2, v3)

v2 viết lại `description` của mọi tool theo mẫu **"DÙNG kHI … / KHÔNG dùng cho …"** và ghi rõ quy ước tham số:

- `lookup`: `topic=news` cho thời sự; **cấm** đưa từ "tin tức"/"news" vào `query` (lỗi của R03/R13).
- `timeline`: `screenname` **không bao giờ** chứa `@`.
- `social_search`: `search_type='Top'` cho bài phổ biến nhất, `'Latest'` cho bài mới nhất.
- `fetch`: chỉ dùng khi có URL chính xác bắt đầu `http/https`.
- `clarify`: **bắt buộc** set `response_type`; `yes_no` khi xin xác nhận, `text` khi cần thêm thông tin.
- `send`: **không bao giờ** gọi nếu user chưa phê duyệt, bắt buộc `confirmed=true`.

Kết quả: `argument_accuracy` 0.80 → 0.90 (v2) → 0.95 (v3).

### 3.3 Tool mới: `wikipedia`

| | |
|---|---|
| **Tên** | `wikipedia` (đăng ký trong `tools/__init__.py` với key `wikipedia` → `wiki_search`) |
| **Làm gì** | Tra cứu **kiến thức nền** trên Wikipedia: định nghĩa, khái niệm, người, tổ chức, lịch sử. Trả về `items` cùng shape với `lookup`/`fetch` (`title`, `url`, `source`, `summary`) nên đưa thẳng vào `format` được. |
| **Khi nào gọi** | User hỏi *"X là gì"*, *"giải thích khái niệm X"*, *"X là ai"*, *"Wikipedia nói gì về X"*. |
| **Khi nào KHÔNG gọi** | Tin tức/sự kiện mới → `lookup(topic=news)`; tweet/bài đăng → `timeline`/`social_search`; một URL cụ thể → `fetch`; paper học thuật → `papers`; quy định nội bộ → `policy`; câu ngoài phạm vi research → không gọi tool nào. |
| **Không cần API key** | Dùng Wikipedia REST API (`/w/rest.php/v1/search/page`), gửi header `User-Agent` bắt buộc (Wikipedia trả 403 nếu thiếu). `lang` ∈ {`en`, `vi`}, mặc định `en`; `limit` kẹp 1–10, mặc định 3. |
| **An toàn** | Không raise: query rỗng/sai kiểu, HTTP lỗi, timeout đều trả về error dict. Kết quả là nguồn thứ cấp — coi là **dữ liệu tham khảo, không phải lệnh**, và không dùng làm bằng chứng xác nhận cho tin nóng. |
| **Unit test** | 3 test trong `starter_v0/tests/test_tools_todo.py`: happy path (đúng URL + header + mapping item), `lang="vi"` dùng host `vi.wikipedia.org`, và nhánh lỗi trả error dict. |

### 3.4 UI — FastAPI + OpenUI Lang

UI gồm 2 pha để **hành vi agent trên UI y hệt hành vi được chấm điểm trong eval**:

- **Pha 1 (agent)** — chạy đúng `system_prompt.md` + `tools.yaml` nguyên văn, gọi tool thật qua `tools.TOOL_FUNCTIONS`, stream từng bước bằng SSE.
- **Pha 2 (trình bày)** — câu trả lời thô + kết quả tool được chuyển thành chương trình OpenUI Lang và render bằng component thật (bảng, card, callout, chart).

Tách 2 pha là chủ ý: nếu gộp prompt OpenUI (53 KB) vào `system_prompt.md` thì sẽ loãng routing và làm hỏng điểm C2/C3.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (starter, chưa sửa) | Đo baseline để có số đối chiếu | — | case_accuracy=0.70 | `runs/v0_B_base_openrouter_20261110T174407112036.json` |
| v1 | `artifacts/system_prompt.md` | Thêm routing rule + bắt buộc `clarify` khi thiếu thông tin → routing đúng hơn | 0.70 | case_accuracy=0.80 | `runs/v1_B_base_openrouter_20261110T180213807365.json` |
| v2 | `artifacts/tools.yaml` | Viết lại `description` theo "khi nào dùng / không dùng" + quy ước args → args đúng hơn | 0.80 | case_accuracy=0.90 | `runs/v2_B_base_openrouter_20261110T181404462799.json` |
| v3 | `artifacts/tools.yaml` | Bắt buộc `clarify` set `response_type` + khai báo tool mới `wikipedia` → args đúng hơn nữa | 0.90 | case_accuracy=0.95 | `runs/v3_B_base_openrouter_20261110T183420347940.json` |

Chi tiết metric đầy đủ (đọc từ `summary` trong từng run JSON):

| Version | case_accuracy | tool_routing | argument | multiturn | provider_error | measured/total |
|---|---:|---:|---:|---:|---:|---|
| v0 | 0.70 | 0.75 | 0.70 | 1.00 | 0 | 20/20 |
| v1 | 0.80 | 1.00 | 0.80 | 1.00 | 0 | 20/20 |
| v2 | 0.90 | 1.00 | 0.90 | 1.00 | 0 | 20/20 |
| v3 | 0.95 | 1.00 | 0.95 | 1.00 | 0 | 20/20 |

Cả 4 run đều hợp lệ theo quy tắc chấm (`provider_error_cases == 0` và `measured_cases == total_cases`). Mỗi version đổi **một** artifact và **một** giả thuyết, hash `prompt_hash`/`tools_hash` ghi trong `starter_v0/artifacts/version_log.csv` khớp với file tương ứng.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là x^3/3 + C…")` | Agent dùng `send` như kênh "trả lời" thay vì từ chối | v1: bỏ câu *"just go ahead and do it"* của starter, thêm rule phải hỏi/xác nhận → **PASS ở v1** |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci(n): …")` | Cùng lỗi: dùng `send` để trả lời câu coding | v1: cùng fix như R08 → **PASS ở v1** |
| R10_missing_handle | missing_info | v0: `timeline(screenname="sama")` — đoán bừa handle<br>v1: `clarify(question="…tên tài khoản…")` — đã hỏi nhưng **thiếu `response_type`** | Thiếu handle nhưng agent đoán "sama" | v1: bắt buộc `clarify` khi thiếu account name → v1 hỏi đúng nhưng thiếu `response_type`; v2 đã set `response_type` → **PASS ở v2** |
| R11_missing_url | missing_info | v0: `fetch(url="https://example.com/article")` — tự bịa URL<br>v1: `clarify(..., response_type="text")` → PASS<br>v2: `clarify(question="…URL…")` — **mất `response_type`** (hồi quy) | Thiếu URL nhưng agent tự bịa URL | v1: bắt buộc `clarify` khi thiếu URL → PASS ở v1; **hồi quy ở v2**; v3 thêm câu *"BẮT BUỘC phải set tham số response_type"* → **PASS ở v3** |
| R13_parallel_web_and_tweets | wrong_arg_value | v0/v1: `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` — nhồi chữ "news" vào `query`, thiếu `topic="news"` | Query bị nhồi chữ "news", thiếu `topic` | v2: `description` của `lookup` cấm đưa "tin tức"/"news" vào `query` → **PASS ở v2** |
| R03_web_news_routing | wrong_arg_value | v1: `lookup(query="AI news", topic="news", timeframe="day")` | Cùng lỗi query với R13 — **hồi quy so với v0** (v0 gửi đúng `query="AI"`) | v2: cùng fix như R13 → **PASS ở v2** |
| R12_confirm_before_send | wrong_boundary | v0: `send(text="Bản tin này")` — gửi không hỏi xác nhận<br>v1: `clarify(question="…")` — thiếu `response_type`<br>v2/v3: `clarify(..., response_type="text")` | Gửi Telegram không xác nhận (v0); sau đó hỏi xác nhận nhưng chọn `response_type="text"` thay vì `"yes_no"` | v2: `description` của `send` nói rõ chỉ dùng khi user đã xác nhận → agent đã hỏi đúng; nhưng **vẫn FAIL ở v3** vì chọn `text` thay vì `yes_no` |

Ma trận PASS/FAIL theo từng version (đọc trực tiếp từ `results[*].result.passed` trong từng run JSON):

| Case ID | v0 | v1 | v2 | v3 |
|---|:--:|:--:|:--:|:--:|
| R03_web_news_routing | PASS | FAIL | PASS | PASS |
| R08_out_of_scope | FAIL | PASS | PASS | PASS |
| R10_missing_handle | FAIL | FAIL | PASS | PASS |
| R11_missing_url | FAIL | PASS | FAIL | PASS |
| R12_confirm_before_send | FAIL | FAIL | FAIL | FAIL |
| R13_parallel_web_and_tweets | FAIL | FAIL | PASS | PASS |
| R14_out_of_scope_coding | FAIL | PASS | PASS | PASS |

Nhóm lỗi ở v0: `out_of_scope` 2 (dùng `send` làm kênh trả lời), `missing_info` 2 (đoán bừa), `wrong_boundary` 1 (gửi không xác nhận), `wrong_tool` 1 (thiếu `topic=news`).

Một quan sát đáng chú ý: **R03 và R11 hồi quy ở v1/v2** — v1 sửa được R08/R14 nhưng làm hỏng R03 (thêm routing rule làm model nhồi chữ "news" vào `query`), v2 sửa R03 nhưng lại làm R11 mất `response_type`. Nhóm ghi lại cả các hồi quy này thay vì chỉ khoe điểm tăng. Lỗi duy nhất còn lại ở v3 là **R12**: agent hỏi xác nhận đúng (đã gọi `clarify`) nhưng chọn `response_type="text"` thay vì `"yes_no"`.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_wikipedia_background_fact | Kiến thức nền (tổng quan khái niệm) → `wikipedia`, không dùng `lookup`/`papers` | `wikipedia` | **PASS** — gọi `wikipedia` |
| G02_wikipedia_vs_lookup_news | Sự kiện có thời điểm → `lookup(topic=news, timeframe=day)`, **không** dùng `wikipedia` | `lookup` | **PASS** — gọi `lookup(topic=news, timeframe=day)` |
| G03_missing_wikipedia_topic | Thiếu đối tượng tra cứu → phải `clarify`, không tự đoán | `clarify(response_type=text)` | **PASS** — gọi `clarify`, không tự chọn chủ đề |
| G04_greeting_no_tool | Lời cảm ơn → trả lời thẳng, không gọi tool nào (kể cả `send`) | `no_tool` | **PASS** — không gọi tool nào |
| G05_out_of_scope_creative_writing | Yêu cầu sáng tác văn học ngoài phạm vi research | `no_tool` (refuse) | **PASS** — không gọi tool nào |
| G06_switch_wikipedia_to_web_news | 3 lượt: đổi nguồn wikipedia→web, khóa `timeframe=day`, `topic=news` | `lookup` | **PASS** — gọi `lookup(topic=news, timeframe=day)` |
| G07_missing_url_then_fetch | 3 lượt: thiếu URL → lượt 2 cấp URL → chỉ đọc link đó | `fetch(url=…)` | **PASS** — gọi `fetch(url=…)` đúng link |
| G08_wikipedia_carryover_query | 3 lượt: giữ tool wikipedia, đổi query, yêu cầu bản tiếng Việt | `wikipedia(query="học máy", lang="vi")` | **PASS** — gọi `wikipedia(query="học máy", lang="vi")` |
| G09_confirmed_send_boundary | 3 lượt: user đã xác nhận rõ → agent phải hành động `confirmed=true`, không hỏi lại | `send(confirmed=true)` | **PASS** — gọi `send(confirmed=true)` |
| G10_wikipedia_plus_news_parallel | 3 lượt: cần cả kiến thức nền lẫn tin mới → gọi **cả hai** tool | `wikipedia` + `lookup(topic=news)` | **PASS** — gọi cả `wikipedia` **và** `lookup(topic=news)` |

**Kết quả run:** `case_accuracy = 1.00` (10/10 PASS), `tool_routing_accuracy = 1.00`, `argument_accuracy = 1.00`, `multiturn_accuracy = 1.00`, `provider_error_cases = 0`, `measured_cases = 10/10` — run hợp lệ theo quy tắc chấm.

- Run file: `starter_v0/runs/v3_B_group_openrouter_20261110T184843874713.json`
- Provider/model: `openrouter` / `openai/gpt-4o-mini` (cùng model với v0–v3)
- Artifact version: `v3+p8b1d8369242a+tff4501744c70` (khớp dòng v3 trong `version_log.csv`)

Bộ 10 case nhóm phủ đủ 6 loại lỗi của `allowed_failure_types` (`wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`) và có **3 case route tới tool mới `wikipedia`** (G01, G08, G10) — thoả yêu cầu của rubric C5.

> Lệnh tái lập:
> `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json`

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | *"Cho mình tổng quan trên Wikipedia về blockchain"* | `wikipedia(query="Blockchain", lang="en")` | `artifact_version = v3+p8b1d8369242a+tff4501744c70` (khớp dòng v3 trong `version_log.csv`) | **PASS** — trả 3 mục từ Wikipedia kèm link thật (`Blockchain`, `Cryptocurrency`, `Fork (blockchain)`) |
| 2 | *"Tóm tắt 5 tweet mới nhất giúp mình"* | *(không gọi tool)* | như trên | **PASS** — thiếu handle nên agent **hỏi lại**: *"Bạn vui lòng cung cấp tên tài khoản Twitter…"*, không đoán bừa |
| 3 | *"Của Elon Musk nhé"* | `timeline(screenname="elonmusk", limit=5)` | như trên | **PASS** — dùng đúng handle, giữ `limit=5` từ lượt 2; tool lỗi vì thiếu `RAPIDAPI_KEY` và agent **báo lỗi thật, không bịa kết quả** |
| 4 | *"Đăng bản tin đó lên Telegram cho tôi"* | `clarify(response_type="yes_no")` | như trên | **PASS** — agent **hỏi xác nhận trước khi gửi**: *"Bạn có thể xác nhận nội dung bản tin…?"*, chưa gọi `send` |

**Transcript chính:** `starter_v0/transcripts/v3_openrouter_20261110T185012964883.transcript.json` — 4 lượt, provider `openrouter`, model `openai/gpt-4o-mini`.

Hai transcript bổ sung (cùng version v3):
- `v3_openrouter_20261110T184912065678.transcript.json` — 4 lượt: wikipedia → hỏi lại → timeline → lookup (gộp tin tức trước khi đăng).
- `v3_openrouter_20261110T184936514496.transcript.json` — 1 lượt: yêu cầu đăng Telegram → `clarify(response_type="yes_no")`.

Cả 3 transcript đều được sinh bằng `python chat.py --provider openrouter --version v3` và **đã commit vào repo** (`starter_v0/transcripts/`).

> ⚠️ Một hạn chế quan sát được: ở lượt 2 agent hỏi lại bằng **text**, không gọi tool `clarify`, vì `chat.py` không ép `tool_choice`. Trong eval thì ngược lại — `run_eval.py` ép `tool_choice="required"` cho các case cần gọi tool, nên `clarify` luôn được gọi. Đây là khác biệt giữa *hành vi thật khi chat* và *hành vi được chấm tự động*, và cũng là lý do eval không thể đo được lỗi "hỏi lại nhưng không dùng tool".

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới `wikipedia` | `starter_v0/tools/wikipedia/tool.py`, `starter_v0/tools/wikipedia/TOOL.md` | Tra cứu kiến thức nền qua Wikipedia REST API, **không cần API key**; trả `items` cùng shape với `lookup`/`fetch` nên đưa thẳng vào `format` | Query rỗng/sai kiểu, HTTP lỗi, timeout → trả **error dict**, không raise. Header `User-Agent` bắt buộc (Wikipedia trả 403 nếu thiếu) |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` — `pytest` → **90 passed, 0 failed, 14 skipped** | 3 test wikipedia: happy path (URL + `User-Agent` + mapping item), `lang="vi"` dùng host `vi.wikipedia.org`, nhánh lỗi trả error dict | Test dùng fixture `fake_http` — **không gọi mạng thật, không tốn credit** |
| UI (lệnh chạy + link dùng thử) | `starter_v0/ui_server.py`, `starter_v0/ui/index.html`, `starter_v0/ui/app.css`, `docs/UI-DEPLOY.md` | FastAPI + OpenUI Lang: SSE stream từng tool call, render component thật (tiêu đề, accordion section có citation, follow-up, sources). Lệnh: `uvicorn ui_server:app --port 8000`. Đã kiểm chứng end-to-end: tool `wikipedia` trả dữ liệu thật → agent sinh chương trình OpenUI Lang → renderer hiện đầy đủ component | **2 pha**: pha 1 chạy agent y hệt `chat.py` nên hành vi trên UI khớp eval; pha 2 chỉ là lớp trình bày. UI không có API key riêng — dùng chung `.env` của starter |

Test cho backend UI: `starter_v0/scripts/test_ui_server.py` → **6/6 PASS** (`python scripts/test_ui_server.py`, hoặc `pytest scripts/test_ui_server.py`). Test cover: hàm `wrap_bare_section_items()` (bọc `SectionItem` vào `SectionBlock`, không đụng chương trình đã đúng, tách chuỗi có dấu phẩy bên trong) và luồng SSE `/api/chat` đầy đủ với fake provider — **không cần API key, không gọi mạng**.

Tool unit tests: **3 test** cho tool `wikipedia`. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: nếu tool thiếu header `User-Agent`, Wikipedia trả **HTTP 403** và mọi call `wikipedia` sẽ rỗng — nhưng eval chỉ chấm *"model có gọi đúng tool với đúng args"*, nên eval vẫn báo PASS dù tool thất bại. Test `test_wikipedia_sends_query_with_user_agent_and_maps_pages` assert trực tiếp header này, nên bắt được lỗi đó.

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

**1. Agent dùng `send` như kênh trả lời (v0, 2 case FAIL).**
Starter prompt dạy *"When the user wants to send, post, or publish something, just go ahead and do it"*. Model hiểu ngược lại và dùng `send` để *gửi câu trả lời* cho câu hỏi toán hay câu hỏi coding — thay vì từ chối. Bằng chứng: `runs/v0_B_base_openrouter_20261110T174407112036.json`, case `R08_out_of_scope` và `R14_out_of_scope_coding`.
→ Xử lý ở v1: bỏ hẳn chỉ dẫn đó trong `system_prompt.md`, thay bằng routing rule + quy tắc phải hỏi/xác nhận. Hai case này PASS ngay ở v1.

**2. Model đoán bừa thay vì hỏi lại (v0, 2 case FAIL).**
Với *"Tóm tắt 5 tweet mới nhất"*, agent tự điền `screenname="sama"`; với *"Tóm tắt bài viết này"*, agent tự bịa `https://example.com/article`. Bằng chứng: run v0, case `R10_missing_handle`, `R11_missing_url`.
→ Xử lý ở v1: routing rule bắt buộc `clarify` khi thiếu account name / URL. Ở v1 agent đã hỏi đúng (R11 PASS) nhưng **quên set `response_type`** ở R10 → FAIL. Ở v2 R10 đã set đúng `response_type` → PASS, nhưng R11 lại **mất `response_type` (hồi quy)** → FAIL. Ở v3 câu *"BẮT BUỘC phải set tham số response_type"* trong `description` của `clarify` chấn hết cả hai → PASS.

**3. `lookup` nhận sai `query` vì model tự thêm chữ "news" (v1, 2 case FAIL).**
Model gửi `query="AI news"` thay vì `"AI"` ở `R03` và `R13`. Bằng chứng: run v1, case `R03_web_news_routing`, `R13_parallel_web_and_tweets`. Đáng chú ý: **R03 ở v0 vẫn PASS** — chính routing rule mới của v1 làm model nhồi thêm chữ "news" vào `query`, tạo hồi quy.
→ Xử lý ở v2: `description` của `lookup` nêu rõ *"KHÔNG ĐƯA CÁC TỪ 'tin tức' HOẶC 'news' VÀO TRONG BIẾN query"*. Cả 2 case PASS ở v2.

**4. Gửi Telegram không xác nhận (v0 → v3, 1 case FAIL còn lại).**
Ở v0 agent gọi `send(text="Bản tin này")` ngay khi chưa có xác nhận. Ở v2–v3 agent đã hỏi xác nhận đúng, nhưng chọn `response_type="text"` thay vì `"yes_no"` → vẫn FAIL ở v3 (`R12_confirm_before_send`).
→ Đây là lỗi **còn lại** của v3, ghi trung thực trong B2 thay vì che. Hướng sửa vòng sau: thêm ví dụ cụ thể vào `description` của `clarify` (*"khi xin xác nhận gửi/đăng thì dùng `response_type='yes_no'"*) hoặc đưa quy tắc này vào `system_prompt.md`.

**5. UI: OpenUI Lang sinh ra component nhưng không phải lúc nào cũng đúng.**
Lần đầu dùng OpenUI, 2 component không hiện (`TagBlock`, `MetricIndicator`) — nguyên nhân là **dùng sai signature** (`TagBlock` nhận *mảng* string, không nhận 3 string riêng lẻ; chat library không có `MetricIndicator`, chỉ có `MetricIndicatorInline`). Không phải bug của thư viện.
→ Kiểm chứng bằng cách render từng component riêng (7/7 component render đúng, 0 lỗi JS), rồi sửa signature trong prompt đưa cho model.

**6. UI: theme sáng/tối của OpenUI bị đảo ngược.**
OpenUI dùng `@media (prefers-color-scheme: dark)` để đảo theme. Trên máy cài theme tối, OpenUI đảo sang bản sáng trong khi nền trang vẫn tối → chữ gần như vô hình.
→ Sửa bằng attribute `data-openui-theme="light"` trên thẻ `<html>` (OpenUI có sẵn cơ chế này) và nền sáng cho vùng render component.

**7. Ràng buộc đề: "Bắt buộc có UI chạy được bằng Streamlit hoặc Vercel".**
`README.md` ghi *"Streamlit hoặc Vercel"*, còn `CHECKPOINTS.md` ghi *"Streamlit, Vercel hoặc khác"*. Nhóm chọn **FastAPI + OpenUI Lang** (React) và dựng được UI dùng được ngay.
→ Xử lý: hướng dẫn deploy đã ghi trong `docs/UI-DEPLOY.md` cho cả hai đường — Cloudflare Tunnel (chạy ngay) và Vercel (Python serverless) — để UI nằm trong những gì đề chấp nhận. Ưu tiên deploy Vercel nếu còn thời gian.

**8. Máy bị đầy ổ đĩa khi cài dependency.**
Ban đầu ổ `D:` chỉ còn vài MB trống, `pip install` thất bại với *"No space left on device"*.
→ Xử lý: đặt virtualenv ở ổ `C:` (`C:\Users\tiniv\.venvs\research-agent`) thay vì trong repo; dọn thư mục `pip-*` tạm còn sót. Repo chỉ chứa mã nguồn, không chứa `.venv`.

**9. Live chat hỏi lại bằng text, không dùng tool `clarify` (phát hiện khi đọc transcript).**
Trong transcript `v3_openrouter_20261110T185012964883.transcript.json`, ở lượt 2 (*"Tóm tắt 5 tweet mới nhất"*) agent **không gọi `clarify`** mà trả lời bằng text thuần: *"Bạn vui lòng cung cấp tên tài khoản Twitter…"*. Hành vi đúng về mặt nghiệp vụ (hỏi thay vì đoán) nhưng **không đi qua tool**, nên không tạo được `awaiting_user` flag mà `chat.py` dùng để dừng vòng lặp.
→ Nguyên nhân: `chat.py` không ép `tool_choice`, còn `run_eval.py` ép `tool_choice="required"` cho các case cần gọi tool. Đây là **khác biệt giữa hành vi thật khi chat và hành vi được chấm tự động** — ghi lại trung thực thay vì giấu. Nhóm ghi vào B4 và B6 để người chấm hiểu giới hạn của cách chấm.

**10. Thiếu API key cho tool `timeline` / `lookup` trong lúc chạy live chat.**
`TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY` đang rỗng trong `.env`, nên `timeline` và `lookup` trả error dict.
→ Xử lý: agent **báo lỗi thật và không bịa kết quả** — đây đúng là hành vi rubric C6 đòi ("UI che lỗi tool thì không tính"). Transcript vẫn dùng được làm bằng chứng vì phần cần chứng minh là *routing + hỏi lại + xác nhận*, không phải nội dung tool. Khi demo, điền đủ key sẽ có kết quả thật.

**11. OpenUI: nội dung chính bị mất khi model đặt `SectionItem` sai chỗ.**
Lần đầu chạy UI, phần lớn câu trả lời **không hiện** — chỉ còn tiêu đề *"Related Queries"* và các follow-up. Nguyên nhân: `SectionItem` chỉ render được khi nằm **bên trong** `SectionBlock`; model (đặt `SectionItem` trực tiếp vào `Card`) làm parser *"permissive"* bỏ qua nó.
→ Thử 1: thêm rule vào OpenUI prompt (*"KHÔNG đặt `SectionItem` trực tiếp vào `Card`"*) — **model nhỏ không tuân theo**, vẫn sai.
→ Thử 2: dùng model mạnh hơn cho pha trình bày — tốn credit, không bảo đảm.
→ Xử lý cuối: **sửa ở backend** — hàm `wrap_bare_section_items()` trong `ui_server.py` tự động gom các `SectionItem` đặt trực tiếp trong `Card` vào một `SectionBlock`. Có 3 unit test riêng cho hàm này trong `scripts/test_ui_server.py`. Sau khi sửa, UI hiển thị đầy đủ: tiêu đề, 3 mục dạng accordion (mục đầu mở sẵn, có citation `[1]`), follow-up và sources.

**12. CSS: nền tối làm chữ OpenUI không đọc được.**
`.msg-assistant .bubble` (2 class) có độ ưu tiên cao hơn `.bubble-ui` (1 class), nên nền trắng của vùng render bị ghi đè bằng nền tối, trong khi component OpenUI dùng theme sáng → chữ gần như vô hình.
→ Sửa bằng cách nâng độ ưu tiên rule: `.msg-assistant .bubble-ui`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân trong `report/team/`.

| Thành viên | Phần việc | File sở hữu chính |
|---|---|---|
| Nhóm trưởng | Setup, chạy v0–v3, `version_log.csv`, bảng B1/B2, gom bài | `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/` |
| Vương Quang Thắng (2A202603855) | Sửa `system_prompt.md` + `tools.yaml` qua 3 vòng, đặt giả thuyết mỗi version | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml` |
| Nguyễn Tài minh Huy (2A202603828) | Viết tool `wikipedia`, đăng ký registry, unit test | `starter_v0/tools/wikipedia/`, `starter_v0/tests/test_tools_todo.py` |
| Vũ Văn Trường (2A202603910) | 10 eval case của nhóm, UI FastAPI + OpenUI, transcript, Phần A + poster, hỗ trợ Phần B | `starter_v0/data/eval_group.json`, `starter_v0/ui_server.py`, `starter_v0/ui/`, `starter_v0/transcripts/`, `report/team/` |

## 7. Hạn chế và hướng cải thiện — B6. Reflection

**Fix nào thuộc `system_prompt.md`?**
Ở v1: bỏ 4 chỉ dẫn xấu có sẵn của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép làm trong một bước, chỉ được chọn một tool), thay bằng routing rule cho 5 tool và quy tắc bắt buộc `clarify` khi thiếu URL / account name. Hiệu quả rõ nhất: `tool_routing_accuracy` 0.75 → **1.00** ngay ở v1, và 2 case `out_of_scope` chuyển FAIL → PASS.

**Fix nào thuộc `tools.yaml`?**
Ở v2 và v3. Cùng một file nhưng hai giả thuyết khác nhau:
- v2 — *tool declaration*: viết lại `description` theo "DÙNG KHI / KHÔNG dùng cho" + quy ước args (cấm "news" trong `query`, `screenname` không có `@`, `search_type` Top/Latest). Giúp `argument_accuracy` 0.80 → 0.90.
- v3 — *ràng buộc tham số*: bắt buộc `clarify` set `response_type`, bắt buộc `send` set `confirmed=true`, và khai báo tool mới `wikipedia` kèm ranh giới rõ với `lookup`. Giúp 0.90 → 0.95.

Bài học: **cùng một file, hai loại fix khác nhau** — một loại là *định hướng* (giúp model chọn đúng tool), một loại là *định dạng tham số* (giúp model truyền đúng args). `prompt_hash` vẫn giữ nguyên ở v2 và v3, chỉ `tools_hash` đổi — nên version log ghi rõ từng lần.

**Failure nào cần review thủ công thay vì chấm tự động?**
- `R12_confirm_before_send`: eval chỉ so `response_type`, nên "hỏi xác nhận bằng `text`" bị tính là FAIL dù hành vi gần đúng. Cần người đọc hiểu mức độ "gần đúng".
- `R08`/`R14` ở v0: agent gửi **đúng câu trả lời** qua `send` — người đọc phải hiểu đây là lỗi *hành vi*, không phải lỗi *nội dung*.
- Các case `no_tool` (R08/R09/R14 và G04/G05): eval chỉ kiểm "không gọi tool", **không** kiểm câu trả lời có hữu ích hay không. Một agent trả lời sai mà không gọi tool vẫn PASS.
- Với `wikipedia`: eval chỉ chấm routing + args, **không** chấm nội dung bài viết có đúng với câu hỏi hay không — đó là lý do unit test cho tool vẫn cần thiết.
- **Khác biệt eval ↔ live chat**: eval ép `tool_choice="required"` cho case cần gọi tool, còn `chat.py` thì không. Vì vậy trong live chat agent có thể hỏi lại bằng text thay vì gọi `clarify` (xem transcript lượt 2) — hành vi này **không bị eval nào phát hiện**. Người đọc transcript phải tự đối chiếu, không nên tin rằng eval đã phủ hết.

**So sánh eval ↔ live chat (điểm nhóm muốn nói rõ):**

| | Eval (`run_eval.py`) | Live chat (`chat.py`) |
|---|---|---|
| `tool_choice` | ép `"required"` khi case cần gọi tool | không ép |
| Thiếu thông tin | luôn gọi `clarify` | có thể hỏi bằng text |
| Đo lỗi "hỏi sai kiểu" | có (so `response_type`) | không, phải đọc tay |
| Kết quả | 20/20 base (v3: 19/20) + 10/10 group | 4 lượt, đủ 3 hành vi C6 yêu cầu |

Nhóm ghi bảng này để **không biến điểm eval thành thứ mà nó không phải**: eval đo routing và args, còn live chat cho thấy agent thật sự hỏi lại và xin xác nhận trước khi hành động.

**Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?**
Vòng v4 sẽ nhắm đúng lỗi còn lại (`R12`): thêm vào `description` của `clarify` một quy tắc phân biệt rõ hai tình huống — *"dùng `response_type='yes_no'` khi cần xin xác nhận một hành động (gửi/đăng/xóa), dùng `response_type='text'` khi cần người dùng cung cấp thêm dữ liệu còn thiếu"* — kèm 2 ví dụ cụ thể. Giả thuyết: phần còn lại là **mơ hồ ranh giới giữa "xin xác nhận" và "xin thêm thông tin"**, nên mẫu ngữ cụ thể sẽ giúp model phân biệt tốt hơn câu quy tắc chung. Metric kỳ vọng: `argument_accuracy` 0.95 → 1.00, `case_accuracy` 0.95 → 1.00.

Ngoài ra, nếu có thời gian, nhóm sẽ dùng 3 case nhóm còn lại (G04, G05, G09 — đều là `no_tool` hoặc boundary) để **tự viết thêm unit test cho `send`** vì đó là tool có side effect thật, và làm bonus *Small Local Model* để đo khoảng cách giữa model cloud và model 3B.

## 8. Tài liệu tham khảo

- **OpenUI** — https://openui.com · mã nguồn: https://github.com/thesysdev/openui
  Dùng `@openuidev/react-ui` (0.18.5) để sinh component library và system prompt, `@openuidev/react-lang` (1.1.0) để sinh prompt, `@openuidev/browser-bundle` (0.2.2) để chạy renderer trên trình duyệt không cần build step.
- **FastAPI** — https://fastapi.tiangolo.com · **Uvicorn** — https://www.uvicorn.org
- **Wikipedia REST API** — https://en.wikipedia.org/w/rest.php/v1/search/page (dùng bởi tool `wikipedia` của nhóm)
- **Cloudflare Tunnel** — https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/ (dùng để expose UI local ra link public cho team khác thử)
- **Tài liệu lab**: [README.md](../../README.md) · [RUBRIC.md](../../RUBRIC.md) · [CHECKPOINTS.md](../../CHECKPOINTS.md) · [docs/UI-DEPLOY.md](../../docs/UI-DEPLOY.md)
- **Tài liệu chính thức của các tool có sẵn**: OpenRouter API, Tavily Search, Firecrawl, RapidAPI (Twitter), arXiv API — xem [docs/TOOL-SETUP.md](../../docs/TOOL-SETUP.md)
