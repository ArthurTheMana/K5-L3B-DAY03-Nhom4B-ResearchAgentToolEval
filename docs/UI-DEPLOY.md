# UI & Deploy — Day 03 Lab (vai trò D)

UI là **FastAPI (Python) + OpenUI Lang**. Backend chạy research agent thật (tái dùng
100% code của `starter_v0`), frontend là một trang HTML tĩnh render component
OpenUI. **Không cần Node, không cần build step** khi chạy UI.

```
starter_v0/
  ui_server.py            # FastAPI: /api/chat (SSE), /api/tools, /static
  ui/
    index.html            # frontend React + OpenUI renderer (CDN)
    app.css               # layout chat
    openui_prompt.md      # OpenUI Lang system prompt (sinh sẵn, đã commit)
    spec.json             # component library spec (sinh sẵn, đã commit)
  scripts/
    gen_openui_prompt.mjs # sinh lại openui_prompt.md + spec.json (chỉ khi đổi lib)
    smoke_ui.py           # test backend không cần API key
    test_ui_server.py     # unit test backend (6 test, không cần API key)
```

## 1. Chạy local

```bash
cd starter_v0
pip install -r requirements.txt          # đã có fastapi + uvicorn
uvicorn ui_server:app --port 8000        # → http://127.0.0.1:8000
```

Windows (PowerShell) — nếu dùng venv:

```powershell
cd starter_v0
.\.venv\Scripts\Activate.ps1
uvicorn ui_server:app --port 8000
```

Lệnh hữu ích:

```bash
uvicorn ui_server:app --reload --port 8000   # tự reload khi sửa code
python scripts/smoke_ui.py                    # smoke test backend, không cần API key
python scripts/test_ui_server.py              # unit test backend (6 test), không cần API key
```

## 2. Link dùng thử cho team khác — Cloudflare Tunnel

Nhanh nhất, không cần đăng ký domain, không cần deploy lên cloud.

### 2.1 Chạy UI local trước

```bash
uvicorn ui_server:app --port 8000     # → http://127.0.0.1:8000
```

### 2.2 Cài `cloudflared`

```bash
winget install --id Cloudflare.cloudflared    # Windows
brew install cloudflared                      # macOS
# Linux: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
```

Windows: nếu báo `cloudflared not recognized`, mở terminal mới rồi chạy lại.

### 2.3 Mở tunnel (terminal thứ 2, GIỮ MỞ suốt showdown)

```bash
cloudflared tunnel --url http://localhost:8000
```

Lệnh in ra URL dạng:

```text
https://<random-words>.trycloudflare.com
```

Copy URL đó dán vào mục **A1** của `report/team/group_report.md`.

### 2.4 Lưu ý quan trọng

- Link `trycloudflare.com` là **tạm thời**, sống theo phiên `cloudflared`. Tắt terminal
  2 là mất link → mọi người không mở được nữa.
- Phải giữ **cả 2 terminal** (UI + tunnel) mở trong suốt buổi demo.
- Đây là lab học tập; chỉ expose link khi cần demo, đóng tunnel ngay sau khi
  xong. **Không** commit `.env` hay bất kỳ API key nào.
- Nếu muốn link sống lâu hơn: deploy lên Vercel (Python serverless) hoặc
  Streamlit Cloud, rồi dùng link đó thay cho tunnel.

## 3. Vì sao chọn FastAPI + OpenUI (thay vì Streamlit)

| Tiêu chí | FastAPI + OpenUI | Streamlit |
|---|---|---|
| Tái dùng code agent | 100% (`TOOL_FUNCTIONS`, `providers`) | 100% |
| Hiển thị tool call từng bước | SSE stream, từng event | phải hack qua session state |
| Trình bày kết quả | component thật (bảng, chart, card) | markdown/table thuần |
| Build step | không | không |
| Phụ thuộc thêm | `fastapi`, `uvicorn` | `streamlit` |

Ràng buộc của đề: `README.md` ghi *"Bắt buộc có UI chạy được bằng Streamlit hoặc
Vercel"*, còn `CHECKPOINTS.md` ghi *"Làm UI (Streamlit, Vercel hoặc khác)"*. Vì vậy
nếu đưa UI lên **Vercel** thì hợp lệ với cả hai cách đọc.

## 4. Kiến trúc 2 pha — vì sao OpenUI không làm hỏng eval

Đây là điểm quan trọng nhất của thiết kế:

```
Pha 1 (AGENT — giống hệt chat.py / run_eval.py)
    system_prompt.md (nguyên văn) + tools.yaml (nguyên văn)
    → gọi tool thật → trả lời text thô
    → hành vi GIỐNG HỆT hành vi rubric C2/C3 chấm điểm

Pha 2 (TRÌNH BÀY — chỉ lớp hiển thị)
    câu trả lời thô + kết quả tool
    → prompt OpenUI Lang (ui/openui_prompt.md)
    → chương trình OpenUI Lang
    → Renderer vẽ component
```

Nếu gộp OpenUI prompt vào `system_prompt.md` thì prompt 53 KB của OpenUI sẽ loãng
routing và làm hỏng số điểm eval. Tách 2 pha giữ cho **hành vi agent trên UI y hệt
hành vi được chấm**.

## 5. Sinh lại OpenUI prompt (chỉ khi đổi component library)

File `ui/openui_prompt.md` và `ui/spec.json` **đã commit sẵn** nên không cần node khi
chạy UI. Nếu muốn sinh lại (ví dụ đổi phiên bản OpenUI):

```bash
cd starter_v0
npm install @openuidev/react-ui@0.18.5 @openuidev/react-lang@1.1.0 @openuidev/lang-core@1.1.0
node scripts/gen_openui_prompt.mjs
```

Script sẽ ghi lại `starter_v0/ui/openui_prompt.md` + `starter_v0/ui/spec.json`.

Script còn thêm **rule riêng của nhóm** vào prompt (biến `teamRules`):

- `SectionItem` chỉ được đặt bên trong `SectionBlock`; nội dung chính dùng `TextContent`.
- `CardHeader` ở đầu `Card`, `FollowUpBlock` và khối sources ở cuối.

Lưu ý khi sửa script: `additionalRules` phải đặt **sau** `...openuiChatPromptOptions`,
nếu không `promptOptions` của thư viện sẽ ghi đè và rule của nhóm bị mất.

## 5.1 Vì sao backend còn có `wrap_bare_section_items()`

Dù prompt đã có rule, model nhỏ (`gpt-4o-mini`) vẫn hay đặt `SectionItem` trực tiếp
vào `Card`. Parser của OpenUI là *"permissive"* nên nó **bỏ qua** các `SectionItem`
đó, khiến phần nội dung chính biến mất trên UI (chỉ còn tiêu đề *"Related Queries"*).

Vì vậy backend tự sửa: hàm `wrap_bare_section_items()` gom các `SectionItem` đặt
trực tiếp trong `Card` vào một `SectionBlock` trước khi gửi xuống trình duyệt.
Có unit test riêng trong `scripts/test_ui_server.py`.

## 6. Những gì UI hiển thị (để demo)

| Vị trí | Nội dung |
|---|---|
| Sidebar → Cấu hình | Chọn provider, nhập version label (v3), nút Reset chat |
| Sidebar → Tools | Danh sách tool lấy tự động từ `artifacts/tools.yaml`, bấm để xem params |
| Main | Lịch sử chat; mỗi tool call là card `🔧 <tên>` (bấm để xem args + result) |
| Main | Câu trả lời được render bằng OpenUI component (bảng, card, callout, chart) |
| Main | Mục *"raw text của agent"* — thu gọn câu trả lời gốc của model |

Khi agent gọi tool `clarify`, UI dừng vòng lặp và chờ user trả lời ở lượt tiếp theo
— đúng hành vi của `chat.py`.

## 7. Câu hỏi mẫu để demo

1. `Tin AI hôm nay có gì nổi bật?` → `lookup(topic=news, timeframe=day)`
2. `Tóm tắt 5 tweet mới nhất giúp mình` → **hỏi lại** (thiếu handle)
3. `Của Elon Musk nhé` → `timeline(screenname=elonmusk, limit=5)`
4. `Cho mình tổng quan trên Wikipedia về blockchain` → tool mới của nhóm
5. `Tổng hợp tin hôm nay rồi đăng lên Telegram` → **hỏi xác nhận** trước khi gửi
6. `Giải giúp mình hệ phương trình bậc hai` → từ chối, không gọi tool

## 8. Troubleshooting

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `ModuleNotFoundError: fastapi` | Chưa cài dependency | `pip install -r requirements.txt` |
| Sidebar báo thiếu API key | Chưa có `.env` | Copy `.env.example` → `.env`, điền key |
| Trang trắng, không thấy gì | CDN bị chặn hoặc mất mạng | Kiểm tra mạng; bundle OpenUI load từ jsdelivr |
| Component hiện nhưng chữ quá nhạt | Thiếu `data-openui-theme="light"` trên `<html>` | Kiểm tra thẻ `<html>` trong `ui/index.html` |
| `Port 8000 is already in use` | Đã có app khác chạy | `uvicorn ui_server:app --port 8001` và đổi port trong tunnel |
| Tunnel báo lỗi kết nối | UI local chưa lên | Kiểm tra `http://127.0.0.1:8000` trước, rồi mở tunnel |
| Agent không gọi tool | Prompt chưa có rule routing | Chạy đúng version (`--version` / version label) đã tối ưu |
| Câu trả lời hiện dạng text thay vì component | Model không sinh đúng OpenUI Lang | UI fallback sang text — vẫn dùng được; xem mục *"raw text"* |
