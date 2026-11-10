# Báo cáo cá nhân — Vũ Văn Trường

## 1. Thông tin thành viên

- Họ tên: Vũ Văn Trường
- MSSV: 2A202603910
- Email: tini.vu.0@gmail.com
- GitHub: `Sz3RO`
- Phần việc phụ trách: **CP4 — Eval của nhóm** và **CP5 — UI + demo** (mục 2 và 3 bên dưới)

## 2. Phần việc phụ trách

Tôi phụ trách ba việc chính trong nhóm:

1. **Viết bộ eval của nhóm** (`starter_v0/data/eval_group.json`) — 10 case: 5 single turn và 5 multi turn, trong đó có 3 case kiểm tra việc agent route tới tool `wikipedia` mà một bạn khác trong nhóm viết.
2. **Xây UI cho agent** (`starter_v0/ui_server.py` + `starter_v0/ui/`) — FastAPI phía Python, frontend là một trang HTML tĩnh render component OpenUI, không cần build step.
3. **Chạy live chat và làm báo cáo** (`starter_v0/transcripts/`, `report/team/`) — 3 transcript để chứng minh agent thật sự hỏi lại và xin xác nhận trước khi hành động; Phần A của báo cáo nhóm và poster. Ở Phần B, tôi phụ trách **B3 (10 case eval của nhóm)** và **B4 (bằng chứng live chat)**; các mục B1/B2/B5a và mục 3, 5, 6, 7, 8 do nhóm trưởng và các bạn khác viết.

## 3. Đóng góp cụ thể

### 3.1 Bộ eval của nhóm (10 case)

Tôi đọc kỹ 6 case FAIL trong run v0 để biết agent thật sự sai ở đâu, rồi mới viết case — không nghĩ case theo cảm tính. Bộ 10 case phủ đủ 6 loại lỗi:

| Loại lỗi | Case kiểm tra |
|---|---|
| `wrong_tool` | G01 (kiến thức nền → `wikipedia`, không phải `lookup`), G06 (đổi nguồn wikipedia→web), G10 (cần cả `wikipedia` lẫn `lookup`) |
| `wrong_arg_value` | G08 (giữ `query` qua lượt, thêm `lang="vi"`), G02 (`topic=news`, `timeframe=day`) |
| `wrong_boundary` | G09 (user đã xác nhận rõ → phải `send(confirmed=true)`, không hỏi lại) |
| `missing_info` | G03 (thiếu đối tượng tra cứu → `clarify`), G07 (thiếu URL → bổ sung rồi `fetch`) |
| `unnecessary_tool` | G04 (lời cảm ơn → không gọi tool nào) |
| `out_of_scope` | G05 (yêu cầu sáng tác văn học → từ chối) |

Hai điều tôi học được khi viết eval:

- `expect.args` được so sánh kiểu **subset** — chỉ những key có trong `expect` mới được kiểm. Nên nếu kỳ vọng model truyền `limit` mà không chắc nó có set hay không thì **không nên** đưa `limit` vào `expect`, nếu không case fail oan.
- Tool gọi **thừa** cũng bị tính FAIL. Vậy `expect` phải liệt kê **đúng bằng** số tool agent nên gọi, không thêm bớt.

Một case tôi phải sửa lại sau khi đọc code của `run_eval.py`: G08 ban đầu kỳ vọng `query="học máy"`, nhưng tool `wikipedia` mặc định `lang="en"` nên model rất dễ viết `"machine learning"` → fail oan. Tôi sửa lượt 2 thành *"dùng bản tiếng Việt"*, giờ cả `query` lẫn `lang` đều xác định.

### 3.2 UI — Streamlit (chính) và FastAPI + OpenUI Lang (nâng cao)

Đây là phần tôi tốn nhiều thời gian nhất và cũng là chỗ dễ làm hỏng cả bài.

**Quyết định thiết kế quan trọng nhất: tách phần agent ra khỏi phần trình bày.**

```
Pha 1 (agent)      system_prompt.md + tools.yaml NGUYÊN VĂN  → gọi tool thật → trả lời text thô
Pha 2 (trình bày)  câu trả lời thô + kết quả tool → hiển thị (Streamlit) hoặc OpenUI Lang (FastAPI)
```

Lý do: prompt OpenUI dài 53 KB. Nếu đưa vào thẳng `artifacts/system_prompt.md` thì prompt sẽ bị loãng và **hỏng luôn số điểm eval** mà nhóm đang cố cải thiện. Tách ra thì hành vi agent trên cả hai UI **y hệt** hành vi được chấm điểm — đây là điều tôi muốn khẳng định với coach.

**UI chính — Streamlit (`app.py`):** đúng lệnh đã ghi ở mục A1 của báo cáo nhóm (`streamlit run app.py`), nên khớp ràng buộc *"UI chạy được bằng Streamlit hoặc Vercel"* của đề.

- Tool loop được **copy nguyên văn** từ `chat.py` (nguồn chuẩn của starter) → hành vi giống hệt `chat.py` và `run_eval.py`.
- Sidebar: chọn provider, version label, hiện danh sách 11 tool lấy tự động từ `artifacts/tools.yaml`, cảnh báo nếu thiếu API key.
- Mỗi tool call hiện thành `st.expander` (tên tool + args + kết quả thật).
- Tool `clarify` trả `awaiting_user: True` → app **dừng vòng lặp** và chờ trả lời ở lượt sau, đúng như `chat.py`.
- Mỗi phiên chat ghi ra `transcripts/<...>.transcript.json` — cùng định dạng với `chat.py` nên dùng làm bằng chứng rubric C6.

**UI thứ hai — FastAPI + OpenUI Lang (`ui_server.py`):** model sinh *component thật* (accordion, bảng, citation, sources) thay vì markdown, đẹp hơn cho showdown.

- Dùng `@openuidev/browser-bundle` từ CDN nên **không cần Node/npm/Vite** khi chạy UI.
- `ui/openui_prompt.md` và `ui/spec.json` được **sinh sẵn và commit vào repo**, nên người khác clone về chạy UI không cần cài node.
- Backend tái dùng nguyôn `tools.TOOL_FUNCTIONS` và `providers` của starter, không viết lại tool nào.
- Tool call được stream bằng SSE nên trên UI thấy được từng bước: agent gọi tool nào, args gì, kết quả ra sao.

Cả hai UI dùng chung một lõi agent, nên **không có chuyện UI này khác UI kia** — chỉ khác lớp hiển thị.

### 3.3 Ba lỗi tôi phát hiện và sửa trong lúc làm UI OpenUI

Cả ba đều là lỗi thật, không phải lỗi "trông cho đẹp":

1. **UI mất khoảng 80% nội dung.** `SectionItem` chỉ render được khi nằm bên trong `SectionBlock`, nhưng model đặt nó trực tiếp vào `Card` nên parser của OpenUI bỏ qua — chỉ còn tiêu đề *"Related Queries"*. Tôi thử thêm rule vào prompt trước, nhưng model nhỏ (`gpt-4o-mini`) **không tuân theo**, nên cuối cùng tôi sửa ở backend: hàm `wrap_bare_section_items()` tự gom các `SectionItem` đặt sai chỗ vào một `SectionBlock`.
2. **Chữ trong vùng render OpenUI không đọc được.** `.msg-assistant .bubble` (2 class) đè `.bubble-ui` (1 class), nên nền tối của app đè nền trắng của component, trong khi OpenUI dùng theme sáng. Sửa bằng cách nâng độ ưu tiên selector.
3. **Rule của nhóm bị mất khi sinh prompt.** Trong script sinh OpenUI prompt, `...openuiChatPromptOptions` được spread sau nên ghi đè mất `additionalRules` của tôi. Sửa lại thứ tự spread.

Cả ba đều được ghi lại ở mục 5 (Khó khăn) của báo cáo nhóm kèm cách xử lý, không giấu đi.

### 3.4 Báo cáo

Tôi viết Phần A (A1/A2/A3) và poster `report/team/poster.html`. Ở Phần B, tôi phụ trách **B3 (10 case eval của nhóm)** và **B4 (bằng chứng live chat)**; các mục B1/B2/B5a và mục 3, 5, 6, 7, 8 do nhóm trưởng và các bạn khác viết.

Riêng bảng B2 tôi ghi lại **cả các hồi quy** chứ không chỉ đường đi tăng điểm: `R03` fail ở v1 (do chính routing rule mới làm model nhồi chữ "news" vào `query`) và `R11` fail ở v2 (mất `response_type`). Lý do là rubric C3 ghi rõ *"version không tăng điểm vẫn được tính nếu phân tích trung thực"* — che giấu hồi quy thì mất điểm chứ không thêm được điểm.

## 4. Bằng chứng

### 4.1 File và commit

| Nội dung | File |
|---|---|
| 10 eval case của nhóm | `starter_v0/data/eval_group.json` |
| **UI chính (Streamlit)** | `starter_v0/app.py` |
| Backend UI OpenUI | `starter_v0/ui_server.py` |
| Frontend UI OpenUI | `starter_v0/ui/index.html`, `starter_v0/ui/app.css` |
| OpenUI prompt + spec (sinh sẵn) | `starter_v0/ui/openui_prompt.md`, `starter_v0/ui/spec.json` |
| Script sinh lại prompt | `starter_v0/scripts/gen_openui_prompt.mjs` |
| Smoke test UI Streamlit | `starter_v0/scripts/smoke_streamlit.py` |
| Unit test backend OpenUI | `starter_v0/scripts/test_ui_server.py` |
| Smoke test backend OpenUI | `starter_v0/scripts/smoke_ui.py` |
| Hướng dẫn chạy UI + deploy | `README.md` (mục *"Deploy nhanh để team khác dùng thử"*) |
| Run eval nhóm | `starter_v0/runs/v3_B_group_openrouter_20261110T184843874713.json` |
| Transcript live chat | `starter_v0/transcripts/v3_openrouter_20261110T185012964883.transcript.json` (+ 2 file nữa) |
| Báo cáo nhóm + poster | `report/team/group_report.md`, `report/team/poster.html` |

Commit của tôi:
- `83e16aa` — merge UI + bộ eval của nhóm
- `8d63909` — sửa case G08 (chốt `lang="vi"` để args xác định)
- `4e3ed92` — chạy suite group (10/10 PASS) + 3 transcript live chat
- `d4f844a` — sửa UI OpenUI (bọc `SectionItem` vào `SectionBlock`, sửa theme)
- `bd960e8` — tạo báo cáo cá nhân này
- `5291fab` — điền B3/B4 vào báo cáo nhóm, gỡ phần gán công việc của các bạn khác

### 4.2 Số liệu đo được

| Hạng mục | Kết quả |
|---|---|
| Run eval nhóm (v3, `openrouter` / `openai/gpt-4o-mini`) | `case_accuracy = 1.00` (10/10 PASS), `tool_routing = 1.00`, `argument = 1.00`, `multiturn = 1.00`, `provider_error_cases = 0`, `measured_cases = 10/10` |
| `pytest` toàn repo | **90 passed, 0 failed**, 14 skipped (14 skip là stub của tool có sẵn, thuộc phần việc của bạn C) |
| `scripts/smoke_streamlit.py` | **PASS** — tool loop gọi đúng `wikipedia`, nhánh `clarify` dừng đúng (`waiting_for_user`), transcript ghi/đọc được |
| `scripts/test_ui_server.py` | **6/6 PASS** |
| `scripts/smoke_ui.py` | **PASS** |
| UI end-to-end | Tool `wikipedia` trả dữ liệu thật từ Wikipedia → agent sinh chương trình OpenUI Lang → renderer hiện đủ tiêu đề, 3 mục accordion có citation `[1]`, follow-up và sources |

### 4.3 Công cụ AI đã dùng và cách tôi tự kiểm tra kết quả

Theo [RULES.md](../../RULES.md), tôi ghi lại công cụ AI đã dùng và cách tự kiểm tra:

| Công cụ | Dùng để | Cách tôi tự kiểm tra |
|---|---|---|
| Trợ lý AI (DeepSeek Harness) | Đọc code starter, thiết kế kiến trúc 2 pha cho UI, viết `app.py` (Streamlit) / `ui_server.py` / `index.html` / `app.css`, viết 10 eval case, viết unit test, sinh và chỉnh OpenUI prompt, viết Phần A/B của báo cáo | **Tôi không tin lời AI** — mọi claim đều kiểm chứng bằng lệnh thật: `pytest` (90 passed), `scripts/smoke_streamlit.py` (PASS), `scripts/test_ui_server.py` (6/6), `scripts/smoke_ui.py` (PASS), `run_eval.py --suite group` (10/10, `provider_error_cases=0`), và render UI bằng trình duyệt headless để **chụp ảnh xác nhận bằng mắt**. Riêng báo cáo thì tôi đối chiếu **từng số liệu** với `runs/*.json` bằng script, phát hiện và sửa 2 chỗ bị viết sai |
| OpenAI GPT-4o-mini (qua OpenRouter) | Model sinh câu trả lời và chương trình OpenUI Lang | Chạy trên bộ eval cố định 20 case và bộ nhóm 10 case; mọi metric đọc từ trường `summary` trong run JSON |
| Wikipedia REST API | Nguồn dữ liệu cho tool `wikipedia` | Gọi thật từ máy, kiểm tra item trả về, URL và header `User-Agent` |

**Ghi nguồn thư viện bên ngoài** (theo [RULES.md](../../RULES.md), *"Ghi nguồn khi dùng code, dữ liệu hoặc tài liệu từ bên ngoài"*):

| Thư viện | Phiên bản | License | Nguồn | Dùng để |
|---|---|---|---|---|
| Streamlit | ≥1.30.0 | Apache-2.0 | https://streamlit.io | UI chính (`app.py`) |
| OpenUI (`@openuidev/react-ui`, `@openuidev/react-lang`, `@openuidev/browser-bundle`) | 0.18.5 / 1.1.0 / 0.2.2 | MIT | https://github.com/thesysdev/openui | Component library + OpenUI Lang prompt cho UI thứ hai |
| FastAPI · Uvicorn | ≥0.110.0 · ≥0.27.0 | MIT | https://fastapi.tiangolo.com · https://www.uvicorn.org | Backend UI OpenUI, stream SSE |
| `htm` | 3.1.1 | Apache-2.0 | https://github.com/developit/htm | Viết React không cần bước build |

Nguyên tắc tôi đặt ra và giữ suốt bài: **mọi dòng trong báo cáo phải truy được về một file hoặc commit cụ thể; không ghi metric, transcript hay commit mà tôi không tự chạy ra.** Trước khi commit tôi cũng đã quét `runs/` và `transcripts/` để chắc chắn không rò rỉ API key.

## 5. Tự đánh giá

**Tôi tự hài lòng về:**

- Thiết kế kiến trúc 2 pha để UI **không làm hỏng** số điểm eval. Đây là rủi ro lớn nhất của phần tôi phụ trách và đã tránh được.
- Viết eval case dựa trên **dữ liệu thật** — đọc 6 case FAIL của run v0 để biết agent sai ở đâu, thay vì nghĩ case theo cảm tính.
- Kiểm chứng mọi thứ bằng lệnh thật và ảnh chụp màn hình, không tin lời AI.
- Ghi cả hồi quy vào báo cáo thay vì chỉ trình bày đường đi tăng điểm.

**Tôi chưa làm / hạn chế:**

- UI **chưa deploy lên Vercel**, đang dùng Cloudflare Tunnel. Ràng buộc ở `README.md` (*"UI chạy được bằng Streamlit hoặc Vercel"*) đã được đáp ứng theo hướng Streamlit (UI chính là `streamlit run app.py`), nhưng nếu có thời gian thì deploy thêm bản Vercel sẽ chắc chắn hơn.
- Chưa làm bonus *Small Local Model* (Ollama).
- Link dùng thử phụ thuộc phiên `cloudflared` nên không sống lâu — phải giữ terminal mở suốt buổi demo.
- Khi live chat, agent có lúc **hỏi lại bằng text thay vì gọi tool `clarify`**, vì `chat.py` không ép `tool_choice` còn `run_eval.py` thì có. Tôi ghi nhận đây là hạn chế của cách chấm tự động ở mục 7 của báo cáo nhóm, thay vì giấu đi.
- Tôi làm **hai UI** (Streamlit và FastAPI + OpenUI). Khi demo chỉ nên mở **một** UI để không gây rối; UI Streamlit là bản dùng chính, UI OpenUI là bản dự phòng/đẹp hơn cho showdown.

**Một quyết định tôi đã đổi ý:** ban đầu tôi dùng FastAPI + OpenUI làm UI chính, nhưng `README.md` của đề yêu cầu *"UI chạy được bằng Streamlit hoặc Vercel"*. Khi nhóm trưởng thống nhất dùng `streamlit run app.py`, tôi viết lại `app.py` (copy nguyên văn tool loop từ `chat.py`) và giữ lại bản FastAPI + OpenUI làm UI thứ hai. Tốn thêm khoảng 1 giờ nhưng rủi ro rubric C6 về bằng 0.

**Bài học lớn nhất của bài này:** với một lab đo *hành vi* bằng eval tự động, điều quan trọng nhất là **giữ cho UI và eval cùng một hành vi agent**. Vì vậy lớp trình bày phải tách khỏi phần agent, đừng lẫn prompt trình bày vào prompt của agent.
