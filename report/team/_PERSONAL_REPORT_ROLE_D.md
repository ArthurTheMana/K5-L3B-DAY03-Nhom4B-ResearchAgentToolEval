# Báo cáo cá nhân — <HỌ TÊN>-<MSSV>

> Vai trò trong nhóm: **D — Eval nhóm + UI + demo (CP4, CP5)**

## 1. Thông tin thành viên

- Họ tên: `<HỌ TÊN>`
- MSSV: `<MSSV>`
- Email: `<EMAIL>`
- GitHub: `Sz3RO`

## 2. Phần việc phụ trách

- **CP4 — Viết 10 eval case của nhóm** (`starter_v0/data/eval_group.json`): 5 single turn + 5 multi turn, phủ đủ 6 loại `failure_type`, trong đó 3 case kiểm tra việc route tới tool mới `wikipedia` của vai trò C.
- **CP5 — Xây UI** (`starter_v0/ui_server.py`, `starter_v0/ui/`): FastAPI (Python) + OpenUI Lang. Backend tái dùng nguyên `tools.TOOL_FUNCTIONS` và `providers` của starter, stream SSE từng tool call; frontend là một trang HTML tĩnh render component OpenUI, **không cần build step**.
- **CP5 — Chạy live chat** (`starter_v0/transcripts/`): 3 transcript, đủ 3 hành vi rubric C6 yêu cầu (yêu cầu thường, thiếu thông tin rồi bổ sung, yêu cầu gửi/đăng).
- **CP5 — Viết Phần A + poster**: `report/team/group_report.md` mục 2 (A1/A2/A3) và `report/team/poster.html`.
- **Hỗ trợ Phần B**: điền B1/B2/B3/B4/B5a, mục 3 (Giải pháp), mục 5 (Khó khăn), mục 6 (Tổng hợp đóng góp), mục 7 (Reflection), mục 8 (Tài liệu tham khảo) — tất cả số liệu trích trực tiếp từ `runs/*.json` và `transcripts/*.json`.

## 3. Đóng góp cụ thể

### 3.1 Bộ eval case của nhóm (10 case)

| Nhóm lỗi được phủ | Case |
|---|---|
| `wrong_tool` | G01 (wikipedia vs lookup), G06 (đổi nguồn wikipedia→web), G10 (gọi cả wikipedia + lookup) |
| `wrong_arg_value` | G08 (carryover `query` + `lang="vi"`), G02 (`topic=news`, `timeframe=day`) |
| `wrong_boundary` | G09 (user đã xác nhận → phải `send(confirmed=true)`, không hỏi lại) |
| `missing_info` | G03 (thiếu đối tượng tra cứu → `clarify`), G07 (thiếu URL → bổ sung rồi `fetch`) |
| `unnecessary_tool` | G04 (lời cảm ơn → không gọi tool nào) |
| `out_of_scope` | G05 (yêu cầu sáng tác văn học → từ chối) |

Ghi chú thiết kế: `expect.args` chỉ chứa **args cần kiểm** (eval so sánh kiểu *subset*), và mỗi case có **đúng bằng** số tool agent nên gọi — vì eval tính tool gọi thừa là FAIL.

### 3.2 UI — FastAPI + OpenUI Lang

Kiến trúc **2 pha**, đây là quyết định thiết kế quan trọng nhất của vai trò D:

```
Pha 1 (AGENT)      system_prompt.md + tools.yaml NGUYÊN VĂN  → gọi tool thật → trả lời text thô
Pha 2 (TRÌNH BÀY)  câu trả lời thô + kết quả tool → prompt OpenUI Lang → chương trình OpenUI Lang → component
```

**Lý do tách 2 pha:** prompt OpenUI dài 53 KB. Nếu gộp vào `artifacts/system_prompt.md` thì sẽ loãng routing và làm hỏng số điểm rubric C2/C3. Tách ra thì **hành vi agent trên UI y hệt hành vi được chấm điểm trong eval** — có thể khẳng định điều này với coach.

Các quyết định kỹ thuật khác:
- Dùng `@openuidev/browser-bundle` từ CDN → không cần Node/npm/Vite khi chạy UI.
- `ui/openui_prompt.md` và `ui/spec.json` **sinh sẵn và commit vào repo** → chạy UI không cần node.
- Thêm rule riêng của nhóm vào OpenUI prompt qua `scripts/gen_openui_prompt.mjs`.
- `wrap_bare_section_items()` trong backend tự gom `SectionItem` đặt sai chỗ vào `SectionBlock` (vì model nhỏ không tuân theo rule trong prompt).

### 3.3 Phát hiện và sửa 3 lỗi trong quá trình làm

1. **UI mất 80% nội dung** — `SectionItem` đặt trực tiếp vào `Card` bị parser OpenUI bỏ qua. Thử thêm rule vào prompt → model nhỏ không tuân theo → sửa ở backend.
2. **Chữ OpenUI không đọc được** — `.msg-assistant .bubble` (2 class) đè `.bubble-ui` (1 class), nền tối đè nền trắng. Sửa độ ưu tiên selector.
3. **Rule của nhóm bị `promptOptions` ghi đè** khi spread sai thứ tự trong script sinh prompt → rule không vào prompt.

Cả 3 đều được ghi lại ở mục 5 (Khó khăn) của `group_report.md` kèm cách xử lý, không che giấu.

### 3.4 Báo cáo

Điền Phần A (A1/A2/A3) + poster; hỗ trợ điền Phần B (B1–B5a), mục 3, 5, 6, 7, 8. Với B2, nhóm ghi lại **cả các hồi quy** (R03 fail ở v1, R11 fail ở v2) chứ không chỉ khoe điểm tăng — vì rubric C3 nói rõ *"version không tăng điểm vẫn được tính nếu phân tích trung thực"*.

## 4. Bằng chứng

- **File/commit/PR:**
  - `starter_v0/data/eval_group.json` — 10 case eval nhóm
  - `starter_v0/ui_server.py` — backend FastAPI + SSE
  - `starter_v0/ui/index.html`, `starter_v0/ui/app.css` — frontend React + OpenUI renderer
  - `starter_v0/ui/openui_prompt.md`, `starter_v0/ui/spec.json` — prompt + spec sinh sẵn
  - `starter_v0/scripts/gen_openui_prompt.mjs` — script sinh lại prompt
  - `starter_v0/scripts/test_ui_server.py` — 6 unit test backend
  - `starter_v0/scripts/smoke_ui.py` — smoke test backend
  - `starter_v0/runs/v3_B_group_openrouter_20261110T184843874713.json` — run group **10/10 PASS**
  - `starter_v0/transcripts/v3_openrouter_20261110T185012964883.transcript.json` — transcript chính (4 lượt)
  - `report/team/group_report.md`, `report/team/poster.html`
  - Commit: `8d63909` (fix G8), `d917ebe` (Phần B report), `4e3ed92` (group run + transcript), `d4f844a` (fix UI), `83e16aa` (merge UI + eval)

- **Số liệu:**
  - Run group: `case_accuracy = 1.00` (10/10), `tool_routing = 1.00`, `argument = 1.00`, `multiturn = 1.00`, `provider_error_cases = 0`, `measured_cases = 10/10`
  - `pytest`: **90 passed, 0 failed**, 14 skipped
  - `scripts/test_ui_server.py`: **6/6 PASS**
  - `scripts/smoke_ui.py`: **PASS**
  - UI end-to-end đã kiểm chứng: tool `wikipedia` trả dữ liệu thật từ Wikipedia → agent sinh chương trình OpenUI Lang → renderer hiện đủ tiêu đề, 3 mục accordion có citation, follow-up và sources

- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**

  | Công cụ | Dùng để | Cách tự kiểm tra |
  |---|---|---|
  | AI coding assistant (DeepSeek Harness) | Đọc code starter, thiết kế kiến trúc 2 pha, viết `ui_server.py` / `index.html` / `app.css`, viết 10 eval case, sinh và chỉnh OpenUI prompt, viết unit test backend | **Không tin lời AI**: mọi claim đều kiểm chứng bằng lệnh thật — `pytest` (90 passed), `scripts/test_ui_server.py` (6/6), `scripts/smoke_ui.py` (PASS), `run_eval.py --suite group` (10/10, `provider_error_cases=0`), và render UI bằng trình duyệt headless để **chụp ảnh xác nhận bằng mắt** |
  | AI assistant | Viết Phần A/B của `group_report.md` | Đối chiếu **từng số liệu** với `runs/*.json` bằng script; phát hiện và sửa 2 chỗ sai (R03 không fail ở v0; R11 hồi quy ở v2) |
  | OpenAI GPT-4o-mini (qua OpenRouter) | Model sinh câu trả lời và chương trình OpenUI Lang | Chạy trên bộ eval cố định 20 case và bộ nhóm 10 case; mọi metric đọc từ `summary` trong run JSON |
  | Wikipedia REST API | Tool `wikipedia` (vai trò C) | Gọi thật từ máy, kiểm tra item + URL + header `User-Agent` |

  **Nguyên tắc đã áp dụng:** mọi đoạn trong báo cáo đều phải truy được về một file/commit cụ thể; không ghi metric, transcript hay commit mà mình không tự chạy ra. Trước khi commit đã quét `runs/` và `transcripts/` để chắc chắn **không rò rỉ API key**.

## 5. Tự đánh giá

**Đã làm tốt:**
- Thiết kế kiến trúc 2 pha để UI **không làm hỏng** số điểm eval — đây là rủi ro lớn nhất của vai trò D và đã tránh được.
- Viết eval case dựa trên **dữ liệu thật**: đọc 6 case FAIL của run v0 để biết agent thật sự sai ở đâu, thay vì nghĩ case theo cảm tính.
- Kiểm chứng mọi thứ bằng lệnh thật + ảnh chụp màn hình, không tin lời AI.
- Ghi cả hồi quy (R03 ở v1, R11 ở v2) vào báo cáo thay vì chỉ trình bày đường đi tăng điểm.

**Chưa làm / hạn chế:**
- Chưa deploy UI lên Vercel (đang dùng Cloudflare Tunnel) — nên ràng buộc *"UI chạy được bằng Streamlit hoặc Vercel"* của `README.md` chỉ được đáp ứng theo cách đọc rộng của `CHECKPOINTS.md` (*"Streamlit, Vercel hoặc khác"*). Đây là điểm rủi ro cần báo coach.
- Chưa làm bonus *Small Local Model* (Ollama).
- Chưa điền nốt 14 test `skip` còn lại trong `tests/test_tools_todo.py` (bonus Test challenge, 1 điểm) — thuộc vai trò C.
- Khi live chat, agent có lúc **hỏi lại bằng text thay vì gọi tool `clarify`** (vì `chat.py` không ép `tool_choice`). Đây là hạn chế của cách chấm tự động, đã ghi vào mục 7 của group report.
- Link dùng thử phụ thuộc phiên `cloudflared` nên không sống lâu; cần giữ terminal mở suốt buổi demo.

**Bài học:** với bài lab đo *hành vi* bằng eval tự động, điều quan trọng nhất là **giữ cho UI và eval cùng một hành vi agent**. Vì vậy phần trình bày phải tách khỏi phần agent, thay vì đưa prompt trình bày vào prompt của agent.
