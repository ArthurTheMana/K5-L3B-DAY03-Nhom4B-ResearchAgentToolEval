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
2. **Xây UI cho agent** (`starter_v0/app.py`) — Streamlit, chạy bằng `streamlit run app.py`, không cần build step.
3. **Chạy live chat và làm báo cáo** (`starter_v0/transcripts/`, `report/team/`) — 3 transcript để chứng minh agent thật sự hỏi lại và xin xác nhận trước khi hành động; Phần A của báo cáo nhóm. Ở Phần B, tôi phụ trách **B3 (10 case eval của nhóm)** và **B4 (bằng chứng live chat)**; các mục B1/B2/B5a và mục 3, 5, 6, 7, 8 do nhóm trưởng và các bạn khác viết.

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

### 3.2 UI — Streamlit (`app.py`)

Đây là phần tôi tốn nhiều thời gian nhất và cũng là chỗ dễ làm hỏng cả bài.

**Quyết định thiết kế quan trọng nhất: tách phần agent ra khỏi phần trình bày.**

```
Pha 1 (agent)      system_prompt.md + tools.yaml NGUYÊN VĂN  → gọi tool thật → trả lời text thô
Pha 2 (trình bày)  câu trả lời thô + kết quả tool → hiển thị trên UI
```

Lý do: **prompt của agent không được lẫn prompt của lớp trình bày.** Lúc đầu tôi làm UI với OpenUI Lang nên có một prompt trình bày dài 53 KB; nếu gộp nó vào `artifacts/system_prompt.md` thì prompt sẽ bị loãng và **hỏng luôn số điểm eval** mà nhóm đang cố cải thiện. Tách ra thì hành vi agent trên UI **y hệt** hành vi được chấm điểm — đây là điều tôi muốn khẳng định với coach. Bản UI cuối cùng là Streamlit nhưng nguyên tắc tách 2 pha vẫn giữ nguyên: `app.py` chỉ dùng `system_prompt.md` + `tools.yaml` nguyên văn, không thêm chỉ dẫn nào của riêng UI.

**UI là Streamlit** (`starter_v0/app.py`), đúng lệnh đã ghi ở mục A1 của báo cáo nhóm (`streamlit run app.py`), nên khớp ràng buộc *"UI chạy được bằng Streamlit hoặc Vercel"* của đề.

- Tool loop được **copy nguyên văn** từ `chat.py` (nguồn chuẩn của starter) → hành vi giống hệt `chat.py` và `run_eval.py`.
- Sidebar: chọn provider, version label, hiện danh sách 11 tool lấy tự động từ `artifacts/tools.yaml`, cảnh báo nếu thiếu API key.
- Mỗi tool call hiện thành `st.expander` (tên tool + args + kết quả thật) **ngay bên trong** bubble của agent.
- Tool `clarify` trả `awaiting_user: True` → app **dừng vòng lặp** và chờ trả lời ở lượt sau, đúng như `chat.py`.
- Mỗi phiên chat ghi ra `transcripts/<...>.transcript.json` — cùng định dạng với `chat.py` nên dùng làm bằng chứng rubric C6.

**Streaming.** Ban đầu UI chỉ hiện tool call *sau khi cả lượt chạy xong* — người dùng phải chờ mấy chục giây mới biết agent đang làm gì. Tôi đổi tool loop thành **generator** (`stream_tool_loop()`) trả về từng sự kiện ngay khi nó xảy ra, nên giờ:

- **Tool call hiện ngay** khi agent vừa quyết định gọi tool, không phải đợi hết lượt — đây là streaming *thật*, ở tầng sự kiện.
- **Câu trả lời hiện dần** bằng `st.write_stream` (Streamlit 1.67).

Tôi ghi rõ trong code rằng phần chia đoạn câu trả lời chỉ là *hiển thị*: provider của starter chỉ expose `complete()` (không có API token-streaming), nên model đã sinh xong câu trả lời trước khi UI bắt đầu hiện. Tôi không sửa `providers/` của starter vì sửa file đó là rủi ro làm lệch hành vi so với eval.

### 3.3 Hai lỗi tôi phát hiện và sửa trong lúc làm UI

Cả hai đều là lỗi thật, không phải lỗi "trông cho đẹp":

1. **UI mất khoảng 80% nội dung.** `SectionItem` chỉ render được khi nằm bên trong `SectionBlock`, nhưng model đặt nó trực tiếp vào `Card` nên parser của OpenUI bỏ qua — chỉ còn tiêu đề *"Related Queries"*. Tôi thử thêm rule vào prompt trước, nhưng model nhỏ (`gpt-4o-mini`) **không tuân theo**, nên cuối cùng tôi sửa ở backend: hàm `wrap_bare_section_items()` tự gom các `SectionItem` đặt sai chỗ vào một `SectionBlock`.
2. **Chữ trong vùng render không đọc được.** `.msg-assistant .bubble` (2 class) đè `.bubble-ui` (1 class), nên nền tối của app đè nền trắng của component, trong khi thư viện dùng theme sáng. Sửa bằng cách nâng độ ưu tiên selector.

> Hai lỗi trên thuộc về bản UI OpenUI mà tôi đã xoá sau khi nhóm thống nhất dùng Streamlit. Tôi ghi lại ở đây vì đó là bài học thật: **một rule trong prompt không đủ — nếu model nhỏ không tuân theo thì phải sửa ở tầng code.**

Ngoài ra tôi cũng đã xoá bản UI OpenUI (FastAPI + React) và giữ lại **một UI duy nhất là Streamlit**, cho khớp đúng lệnh đã ghi ở mục A1 của báo cáo nhóm và giảm rủi ro rubric C6.

### 3.4 Một hồi quy của v3 tôi phát hiện khi chạy lại eval

Sau khi UI dùng streaming token thật, tôi chạy lại bộ eval nhóm để chứng minh
thay đổi của mình **không ảnh hưởng** điểm số (vì tôi không hề sửa
`providers/`, `chat.py`, `run_eval.py` hay `artifacts/`). Kết quả: **9/10**, G09 fail.

Tôi điều tra và tìm ra nguyên nhân — **không phải do code của tôi, mà do một
bản sửa `artifacts/tools.yaml` lúc 19:52** (commit `49bc1cf`), *sau khi* lần
chạy 10/10 của tôi lúc 18:48:

| Run | Thời điểm | Artifact version | Kết quả |
|---|---|---|---|
| `v3_B_group_openrouter_20261110T184843874713.json` | 18:48 | `v3+p8b1d8369242a+tff4501744c70` | **10/10 PASS** |
| `v3_B_group_openrouter_20261110T222856206150.json` | 22:28 | `v3+p8b1d8369242a+t2c78329968e8` | **9/10** — G09 FAIL |

Hai run chỉ khác **mã băm của `tools.yaml`**; `system_prompt.md` giống hệt — nên
nguyên nhân nằm chắc ở `tools.yaml`.

Bản sửa đó đổi `description` của tool `clarify` thành:

> *"Bất cứ khi nào user yêu cầu 'đăng' hoặc 'gửi' ... bạn PHẢI LUÔN gọi clarify
> với `response_type='yes_no'` ... **KỂ CẢ KHI họ chưa cung cấp nội dung**."*

Câu này mâu thuẫn với boundary của `send` (*"không bao giờ gọi `send` nếu user
chưa phê duyệt"*), nên model **hỏi lại lần nữa** cả khi user đã xác nhận:

```
"failures": ["missing tool call send", "extra tool call clarify"]
```

Điều này trái với `RUBRIC.md` (mục Telegram, 2 điểm) vốn yêu cầu đúng luồng:
*agent hỏi lại → user xác nhận → `send(confirmed=true)`*.

**Cách sửa đề xuất** (thuộc vai trò B — chủ sở hữu `tools.yaml`): thêm vào
`clarify` rằng chỉ hỏi xác nhận **khi user chưa xác nhận**, và nói rõ *"nếu user
đã xác nhận rõ ràng thì gọi `send(confirmed=true)`"*.

> Tôi **không tự sửa** `artifacts/tools.yaml` vì đó không phải file của tôi, và
> rubric C3 còn quy định version không tăng điểm vẫn được tính nếu phân tích
> trung thực — nên đây là phát hiện để nhóm xử lý, không phải để tôi âm thầm
> vá cho đẹp số liệu.

### 3.5 Báo cáo

Tôi viết Phần A (A1/A2/A3). Ở Phần B, tôi phụ trách **B3 (10 case eval của nhóm)** và **B4 (bằng chứng live chat)**; các mục B1/B2/B5a và mục 3, 5, 6, 7, 8 do nhóm trưởng và các bạn khác viết.

Riêng bảng B2 tôi ghi lại **cả các hồi quy** chứ không chỉ đường đi tăng điểm: `R03` fail ở v1 (do chính routing rule mới làm model nhồi chữ "news" vào `query`) và `R11` fail ở v2 (mất `response_type`). Lý do là rubric C3 ghi rõ *"version không tăng điểm vẫn được tính nếu phân tích trung thực"* — che giấu hồi quy thì mất điểm chứ không thêm được điểm.

## 4. Bằng chứng

### 4.1 File và commit

| Nội dung | File |
|---|---|
| 10 eval case của nhóm | `starter_v0/data/eval_group.json` |
| **UI (Streamlit)** | `starter_v0/app.py` |
| Streaming token thật (module riêng, không sửa `providers/`) | `starter_v0/streaming.py` |
| Smoke test UI | `starter_v0/scripts/smoke_streamlit.py` |
| Test thứ tự render + conversation (AppTest) | `starter_v0/scripts/test_render_order.py` |
| Công cụ dump DOM để kiểm tra thứ tự phần tử | `starter_v0/scripts/dump_dom.py` |
| Hướng dẫn chạy UI + deploy | `README.md` (mục *"Deploy nhanh để team khác dùng thử"*) |
| Run eval nhóm | `starter_v0/runs/v3_B_group_openrouter_20261110T184843874713.json` |
| Transcript live chat | `starter_v0/transcripts/v3_openrouter_20261110T185012964883.transcript.json` (+ 2 file nữa) |
| Báo cáo nhóm | `report/team/group_report.md` |

Commit của tôi:
- `83e16aa` — merge UI + bộ eval của nhóm
- `8d63909` — sửa case G08 (chốt `lang="vi"` để args xác định)
- `4e3ed92` — chạy suite group (10/10 PASS) + 3 transcript live chat
- `d4f844a` — sửa UI OpenUI (bọc `SectionItem` vào `SectionBlock`, sửa theme)
- `bd960e8` — tạo báo cáo cá nhân này
- `5291fab` — điền B3/B4 vào báo cáo nhóm, gỡ phần gán công việc của các bạn khác
- `6d99db3` — sửa 4 điểm trong báo cáo cá nhân này + ghi nguồn thư viện
- `6b9484a` — chuyển UI chính sang Streamlit (`app.py`), xoá file `docs/UI-DEPLOY.md` do tôi tự soạn nhưng trùng lặp với mục deploy đã có sẵn trong `README.md`
- `ee788a5` — xoá hẳn bản UI FastAPI + OpenUI, thêm streaming token thật cho `app.py`, sửa 3 lỗi logic render, xoá poster, sửa tiếng Việt thiếu dấu

### 4.2 Số liệu đo được

| Hạng mục | Kết quả |
|---|---|
| Run eval nhóm (v3 lúc 18:48, `openrouter` / `openai/gpt-4o-mini`) | `case_accuracy = 1.00` (10/10 PASS), `tool_routing = 1.00`, `argument = 1.00`, `multiturn = 1.00`, `provider_error_cases = 0`, `measured_cases = 10/10` — artifact `v3+p8b1d8369242a+**tff4501744c70**` |
| Run eval nhóm (v3 lúc 22:28, sau khi `tools.yaml` được sửa lúc 19:52) | `case_accuracy = 0.90` (9/10), `provider_error_cases = 0`, `measured_cases = 10/10` — artifact `v3+p8b1d8369242a+**2c78329968e8**`; **G09 FAIL** (`wrong_boundary`) |
| `pytest` toàn repo | **90 passed, 0 failed**, 14 skipped (14 skip là stub của tool có sẵn, thuộc phần việc của bạn C) |
| `scripts/smoke_streamlit.py` | **PASS** — tool loop gọi đúng `wikipedia`, nhánh `clarify` dừng đúng (`waiting_for_user`), **thứ tự stream** đúng (`tool` → `final`), `chunk_text` giữ nguyên nội dung, transcript ghi/đọc được |
| `scripts/test_render_order.py` | **PASS** — kiểm tra trên DOM thật (AppTest): 2 lượt → 4 chat message, tool card luôn render **trước** câu trả lời, lịch sử lượt 1 giữ nguyên sang lượt 2, transcript ghi đúng 2 lượt |
| UI end-to-end (API key thật) | Gõ *"Cho mình tổng quan trên Wikipedia về blockchain"* → tool `wikipedia` trả dữ liệu thật từ Wikipedia (`Blockchain`, `Cryptocurrency`, `Fork (blockchain)`), agent trả lời có link nguồn |
| Transcript do chính UI sinh | `starter_v0/transcripts/v3_openrouter_20261110T225123602600.transcript.json` — **3 lượt do UI Streamlit sinh**, phủ đủ 3 hành vi rubric C6: (1) yêu cầu thường → `wikipedia` trả dữ liệu thật (`Blockchain`, `Cryptocurrency`, `Fork (blockchain)`), (2) thiếu thông tin → agent hỏi lại vì thiếu tên tài khoản, (3) yêu cầu đăng → `clarify` (`status: waiting_for_user`) |
| | `starter_v0/transcripts/v3_openrouter_20261110T213026001249.transcript.json` — 2 lượt chat thật trên UI: *"HI, chào bạn"* (không gọi tool) và *"Tra cứu giá vàng hôm nay"* (gọi `lookup`, tool trả error dict vì thiếu `TAVILY_API_KEY` — agent báo lỗi thật, không bịa kết quả) |

### 4.3 Công cụ AI đã dùng và cách tôi tự kiểm tra kết quả

Theo [RULES.md](../../RULES.md), tôi ghi lại công cụ AI đã dùng và cách tự kiểm tra:

| Công cụ | Dùng để | Cách tôi tự kiểm tra |
|---|---|---|
| Trợ lý AI (DeepSeek Harness) | Đọc code starter, thiết kế kiến trúc 2 pha cho UI, viết `app.py` (Streamlit), viết 10 eval case, viết unit test, viết Phần A/B của báo cáo | **Tôi không tin lời AI** — mọi claim đều kiểm chứng bằng lệnh thật: `pytest` (90 passed), `scripts/smoke_streamlit.py` (PASS), `run_eval.py --suite group` (10/10, `provider_error_cases=0`), và render UI bằng trình duyệt headless để **chụp ảnh xác nhận bằng mắt**. Riêng báo cáo thì tôi đối chiếu **từng số liệu** với `runs/*.json` bằng script, phát hiện và sửa 2 chỗ bị viết sai |
| OpenAI GPT-4o-mini (qua OpenRouter) | Model sinh câu trả lời và quyết định gọi tool | Chạy trên bộ eval cố định 20 case và bộ nhóm 10 case; mọi metric đọc từ trường `summary` trong run JSON |
| Wikipedia REST API | Nguồn dữ liệu cho tool `wikipedia` | Gọi thật từ máy, kiểm tra item trả về, URL và header `User-Agent` |

**Ghi nguồn thư viện bên ngoài** (theo [RULES.md](../../RULES.md), *"Ghi nguồn khi dùng code, dữ liệu hoặc tài liệu từ bên ngoài"*):

| Thư viện | Phiên bản | License | Nguồn | Dùng để |
|---|---|---|---|---|
| Streamlit | ≥1.30.0 (đã kiểm với 1.67.0) | Apache-2.0 | https://streamlit.io | UI (`app.py`), gồm `st.chat_message`, `st.write_stream` |

Nguyên tắc tôi đặt ra và giữ suốt bài: **mọi dòng trong báo cáo phải truy được về một file hoặc commit cụ thể; không ghi metric, transcript hay commit mà tôi không tự chạy ra.** Trước khi commit tôi cũng đã quét `runs/` và `transcripts/` để chắc chắn không rò rỉ API key.

## 5. Tự đánh giá

**Tôi tự hài lòng về:**

- Thiết kế kiến trúc 2 pha để UI **không làm hỏng** số điểm eval. Đây là rủi ro lớn nhất của phần tôi phụ trách và đã tránh được.
- Viết eval case dựa trên **dữ liệu thật** — đọc 6 case FAIL của run v0 để biết agent sai ở đâu, thay vì nghĩ case theo cảm tính.
- Kiểm chứng mọi thứ bằng lệnh thật và ảnh chụp màn hình, không tin lời AI.
- Ghi cả hồi quy vào báo cáo thay vì chỉ trình bày đường đi tăng điểm.
- Phát hiện được **hồi quy thật của v3** (mục 3.4) bằng cách so sánh mã băm artifact giữa hai lần chạy — cùng prompt, chỉ khác `tools.yaml`.

**Tôi chưa làm / hạn chế:**

- UI **chưa deploy lên Vercel**, đang dùng Cloudflare Tunnel. Ràng buộc ở `README.md` (*"UI chạy được bằng Streamlit hoặc Vercel"*) đã được đáp ứng theo hướng Streamlit (UI chính là `streamlit run app.py`), nhưng nếu có thời gian thì deploy thêm bản Vercel sẽ chắc chắn hơn.
- Chưa làm bonus *Small Local Model* (Ollama).
- Link dùng thử phụ thuộc phiên `cloudflared` nên không sống lâu — phải giữ terminal mở suốt buổi demo.
- Khi live chat, agent có lúc **hỏi lại bằng text thay vì gọi tool `clarify`**, vì `chat.py` không ép `tool_choice` còn `run_eval.py` thì có. Tôi ghi nhận đây là hạn chế của cách chấm tự động ở mục 7 của báo cáo nhóm, thay vì giấu đi.
**Một quyết định tôi đã đổi ý — và đã đổi lần hai:** ban đầu tôi dùng FastAPI + OpenUI làm UI chính, nhưng `README.md` của đề yêu cầu *"UI chạy được bằng Streamlit hoặc Vercel"*. Khi nhóm trưởng thống nhất dùng `streamlit run app.py`, tôi viết lại `app.py` (copy nguyên văn tool loop từ `chat.py`). Sau đó nhóm thống nhất bỏ hẳn bản FastAPI + OpenUI, nên tôi **xoá toàn bộ** (`ui_server.py`, `ui/`, script sinh prompt, 2 file test) và chỉ giữ **một UI duy nhất là Streamlit**. Repo gọn hơn, không còn nhánh/UI thừa, và lệnh chạy khớp 100% với mục A1.

**Điều tôi ấn tượng nhất khi làm UI:** lần đầu chạy UI, tool call chỉ hiện *sau khi cả lượt xong* — phải chờ mấy chục giây mới biết agent đang làm gì, trải nghiệm rất tệ. Tôi đổi tool loop thành generator để yield từng sự kiện ngay khi nó xảy ra. Bài học: **UI tốt không chỉ là "hiển thị đúng", mà là phải phản hồi đúng thời điểm.**

**Một điều tôi làm chưa trọn vẹn:** streaming token của câu trả lời chỉ là *hiển thị theo đoạn*, vì provider của starter chỉ expose `complete()` (không có API token-streaming). Muốn có streaming token thật thì phải sửa `providers/` của starter — tôi không làm vì sửa file đó có rủi ro làm lệch hành vi agent so với eval. Tôi ghi rõ điều này trong code và trong báo cáo thay vì làm cho nó *có vẻ* streaming.

**Bài học lớn nhất của bài này:** với một lab đo *hành vi* bằng eval tự động, điều quan trọng nhất là **giữ cho UI và eval cùng một hành vi agent**. Vì vậy lớp trình bày phải tách khỏi phần agent, đừng lẫn prompt trình bày vào prompt của agent.
