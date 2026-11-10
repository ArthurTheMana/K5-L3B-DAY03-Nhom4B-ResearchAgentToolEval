
# Báo cáo cá nhân – NguyenTaiMinhHuy-2A202603828

## 1. Thông tin thành viên

- **Họ tên:** Nguyễn Tài Minh Huy
- **MSSV:** 2A202603828
- **Email:** nguyentaiminhhuy831975@gmail.com
- **Nhóm:** 4B
- **Vai trò:** Nhóm trưởng (Team Leader)
- **Bài Lab:** Day 03 - Research Agent Tool Eval

## 2. Phần việc phụ trách

Trong bài Lab này, mình đảm nhận vai trò nhóm trưởng, chủ yếu phụ trách thiết lập môi trường, chạy các phiên bản Evaluation, kiểm tra kết quả và phối hợp với các thành viên để hoàn thiện hệ thống Research Agent.

Công việc của mình tập trung vào việc đảm bảo Agent có thể chạy được bằng API thật, theo dõi các lỗi xuất hiện trong quá trình kiểm thử và ghi lại kết quả sau mỗi lần nhóm thay đổi System Prompt hoặc Tool Declaration.

Cụ thể, mình phụ trách những công việc sau:

1. **Environment Setup:** Thiết lập môi trường Python trên Windows, tạo Virtual Environment và cài đặt các thư viện cần thiết.
2. **Provider Preflight:** Cấu hình OpenRouter API và kiểm tra khả năng kết nối với model `openai/gpt-4o-mini`.
3. **Baseline Evaluation:** Chạy phiên bản v0 để xác định kết quả ban đầu của Agent.
4. **Version Evaluation:** Chạy lại Evaluation từ v1 đến v3 sau khi nhận các thay đổi từ thành viên phụ trách Prompt và Tool Declaration.
5. **Failure Analysis:** Kiểm tra các test cases thất bại, xác định nguyên nhân và trao đổi lại với nhóm.
6. **Version Management:** Theo dõi kết quả trong `version_log.csv`, lưu Run JSON và các thông tin liên quan đến từng phiên bản.
7. **Tool Integration:** Kiểm tra việc đăng ký Wikipedia Tool vào hệ thống và chạy Tool Contract Tests.
8. **Team Coordination:** Theo dõi tiến độ, tiếp nhận các phần việc và phối hợp kiểm tra trước khi tích hợp.

Mình không trực tiếp viết phần lớn System Prompt hoặc xây dựng Wikipedia Tool. Vai trò chính của mình là chạy kiểm thử, kiểm tra kết quả thực tế và đảm bảo những thay đổi của nhóm có thể được đánh giá bằng dữ liệu cụ thể.

## 3. Đóng góp cụ thể

### 3.1. Thiết lập môi trường và xử lý lỗi ban đầu

Đầu tiên, mình tiến hành thiết lập môi trường để có thể chạy được project trên máy Windows. Mình sử dụng Python 3.14.3, tạo môi trường ảo `.venv` và cài đặt các thư viện trong `requirements.txt`.

Trong quá trình cài đặt, mình gặp một số vấn đề với Python và PowerShell. Ban đầu, Windows không nhận lệnh `python` dù đã cài đặt Python. Sau khi chuyển sang sử dụng `py`, mình tạo được Virtual Environment nhưng lại gặp lỗi PowerShell không cho phép chạy script kích hoạt môi trường.

Mình giải quyết vấn đề này bằng cách gọi trực tiếp Python Interpreter nằm trong thư mục `.venv`, thay vì phải kích hoạt môi trường qua PowerShell.

Lệnh mình sử dụng để cài đặt thư viện:

    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Sau khi cài đặt xong, mình chạy kiểm thử ban đầu bằng `pytest`:

    .\.venv\Scripts\python.exe -m pytest -q

Kết quả nhận được:

- **62 tests passed**
- **17 tests skipped**
- **0 tests failed**

Theo mình hiểu, 17 tests bị skipped là những phần TODO trong Starter Code mà nhóm cần tiếp tục triển khai hoặc có thể làm thêm để lấy điểm bonus. Vì không có test nào thất bại nên mình tiếp tục sang bước kiểm tra API Provider.

Tiếp theo, mình cấu hình file `.env` và chạy Provider Preflight:

    .\.venv\Scripts\python.exe scripts/preflight_provider.py --provider openrouter

Ở bước này, mình gặp lỗi `Missing API key env var: OPENROUTER_API_KEY`. Sau khi bổ sung API Key, mình tiếp tục gặp lỗi `403 - Key limit exceeded` do giới hạn sử dụng của key.

Sau khi xử lý lại cấu hình API, chương trình đã chạy Preflight thành công với model `openai/gpt-4o-mini`.

Kết quả trả về:

    OK provider=openrouter model=openai/gpt-4o-mini
    tool=timeline
    args={'screenname': 'sama', 'limit': 1}

Kết quả này cho thấy Agent đã có thể kết nối với model và thực hiện Tool Calling. Đây cũng là bước giúp mình xác nhận môi trường đã sẵn sàng trước khi chạy Evaluation chính thức.

### 3.2. Chạy Baseline Evaluation v0

Sau khi hoàn thành phần Setup, mình bắt đầu chạy Baseline v0. Mục đích của bước này là xem Agent ban đầu hoạt động như thế nào trước khi nhóm chỉnh sửa System Prompt hoặc Tool Declaration.

Mình sử dụng bộ 20 test cases có sẵn trong `data/eval_base.json`.

Lệnh thực hiện:

    .\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json

Kết quả Baseline v0:

| Metric | Kết quả |
|---|---:|
| Total Cases | 20 |
| Measured Cases | 20 |
| Passed Cases | 14 |
| Case Accuracy | 70% |
| Tool Routing Accuracy | 75% |
| Argument Accuracy | 70% |
| Multiturn Accuracy | 100% |
| Provider Error Cases | 0 |

Trong 20 test cases, Agent vượt qua 14 cases và thất bại ở 6 cases.

Các cases thất bại gồm:

| Test Case | Failure Type |
|---|---|
| `R08_out_of_scope` | `out_of_scope` |
| `R10_missing_handle` | `missing_info` |
| `R11_missing_url` | `missing_info` |
| `R12_confirm_before_send` | `wrong_boundary` |
| `R13_parallel_web_and_tweets` | `wrong_tool` |
| `R14_out_of_scope_coding` | `out_of_scope` |

Sau khi xem kết quả, mình nhận thấy Agent ban đầu vẫn gặp vấn đề khi xử lý những yêu cầu thiếu thông tin, những câu hỏi nằm ngoài phạm vi Research Agent và những yêu cầu cần gọi nhiều công cụ.

Ngoài ra, case `R12_confirm_before_send` cho thấy Agent chưa xử lý đúng bước xác nhận trước khi gửi nội dung lên Telegram.

Mình gửi lại kết quả Evaluation cho Quang Thắng để bạn có thể dựa vào các cases thất bại mà điều chỉnh System Prompt và Tool Declaration.

Mình cũng giữ lại file Run JSON của v0 để nhóm có thể so sánh với những phiên bản tiếp theo. Theo mình, đây là một bước khá quan trọng vì nếu không có Baseline thì sẽ khó biết những thay đổi sau đó có thực sự cải thiện kết quả hay không.

### 3.3. Chạy Evaluation từ v1 đến v3

Sau khi có kết quả v0, mình tiếp tục phối hợp với Quang Thắng để chạy các phiên bản cải thiện của Agent.

Quy trình mình thực hiện là nhận file System Prompt hoặc Tool Declaration đã được cập nhật, đưa vào project, kiểm tra khi cần thiết rồi chạy lại bộ Evaluation. Sau mỗi lần chạy, mình xem những cases nào PASS hoặc FAIL, ghi lại Accuracy và gửi kết quả cho thành viên phụ trách để tiếp tục điều chỉnh.

Mình sử dụng cùng bộ 20 test cases để có thể so sánh kết quả giữa các phiên bản.

**Bảng kết quả Evaluation:**

| Metric | v0 | v1 | v2 | v3 |
|---|---:|---:|---:|---:|---:|
| Passed Cases | 14/20 | 16/20 | 18/20 | 20/20 | 
| Case Accuracy | 70% | 80% | 90% | 100% | 
| Tool Routing Accuracy | 75% | 100% | 100% | 100% |
| Argument Accuracy | 70% | 80% | 90% | 100% |
| Multiturn Accuracy | 100% | 100% | 100% | 100% |
| Provider Error Cases | 0 | 0 | 0 | 0 |

#### Version v1

Ở phiên bản v1, Quang Thắng cập nhật System Prompt để Agent có hướng dẫn rõ ràng hơn về việc lựa chọn công cụ và hỏi lại khi thiếu thông tin.

Sau khi chạy Evaluation, mình nhận được kết quả **16/20 cases PASS**, tương đương **80% Case Accuracy**.

So với v0, kết quả đã tăng 10 điểm phần trăm. Tuy nhiên, vẫn còn 4 cases thất bại, bao gồm `R03`, `R10`, `R12` và `R13`.

Mình nhận thấy có những cases trước đó PASS nhưng sau khi chỉnh Prompt lại FAIL, ví dụ `R03_web_news_routing`. Điều này giúp mình hiểu rằng việc sửa Prompt không phải lúc nào cũng cải thiện toàn bộ các trường hợp. Một thay đổi có thể giải quyết được lỗi này nhưng lại ảnh hưởng đến trường hợp khác.

#### Version v2

Ở phiên bản v2, Quang Thắng tiếp tục chỉnh sửa `tools.yaml`, bổ sung mô tả rõ ràng hơn cho các công cụ và quy ước truyền tham số.

Một trong những vấn đề được xử lý là cách truyền `query` cho công cụ `lookup`. Chẳng hạn, khi người dùng yêu cầu tìm tin tức AI, Agent cần truyền `query="AI"` và sử dụng `topic="news"`, thay vì đưa cả từ `"news"` vào giá trị của query.

Sau khi chạy Evaluation v2, kết quả đạt **18/20 cases PASS**, tương đương **90% Case Accuracy**.

Hai cases còn thất bại là:

- `R11_missing_url`
- `R12_confirm_before_send`

Cả hai đều liên quan đến cách Agent sử dụng công cụ `clarify`, đặc biệt là tham số `response_type`.

#### Version v3

Ở phiên bản v3, nhóm tiếp tục cải thiện hướng dẫn sử dụng công cụ `clarify`, đặc biệt là cách lựa chọn `response_type` khi cần hỏi thêm thông tin hoặc xin xác nhận trước khi gửi nội dung. Đồng thời, Wikipedia Tool cũng đã được tích hợp vào Tool Declaration.

Trong lần chạy v3 ban đầu, Agent vẫn gặp lỗi ở case `R12_confirm_before_send` do sử dụng `response_type="text"` thay vì `"yes_no"`.

Sau khi nhóm cập nhật lại Tool Declaration, mình chạy lại Base Evaluation v3 với cấu hình mới nhất. Kết quả đạt **20/20 cases PASS**, tương đương **100% Case Accuracy**.

Như vậy, so với Baseline v0, Case Accuracy đã tăng từ 70% lên 100%. Mình vẫn giữ kết quả chạy trước đó để có thể đối chiếu và giải thích quá trình cải thiện.

### 3.4. Phân tích những lỗi gặp phải

Trong quá trình chạy Evaluation, mình nhận thấy các lỗi của Agent không chỉ nằm ở việc chọn sai công cụ mà còn có thể xuất hiện ở cách truyền tham số hoặc xử lý yêu cầu của người dùng.

**Tool Routing Error**

Đây là trường hợp Agent lựa chọn sai công cụ hoặc không gọi đủ các công cụ cần thiết. Ví dụ, một yêu cầu cần tìm thông tin trên cả web và mạng xã hội thì Agent phải biết sử dụng cả `lookup` và `social_search`.

**Argument Error**

Đây là trường hợp Agent chọn đúng công cụ nhưng lại truyền sai giá trị tham số. Một ví dụ mình gặp là Agent truyền `query="AI news"` thay vì `query="AI"` trong khi đã có tham số `topic="news"`.

**Missing Information**

Khi người dùng yêu cầu tóm tắt tweet hoặc một bài viết nhưng chưa cung cấp tên tài khoản hay URL, Agent cần sử dụng `clarify` để hỏi lại thay vì tự đoán thông tin còn thiếu.

**Safety Boundary**

Đây là vấn đề liên quan đến việc Agent phải xin xác nhận trước khi thực hiện một hành động như gửi hoặc đăng nội dung.

Trường hợp mình chú ý nhất là `R12_confirm_before_send`. Ở phiên bản v3, Agent đã gọi đúng `clarify` nhưng lại truyền:

    response_type="text"

Trong khi bộ Evaluation mong đợi:

    response_type="yes_no"

Đến v3, case này đã PASS.

Qua trường hợp này, mình hiểu rằng Tool Calling không chỉ là chọn đúng tên công cụ. Agent còn phải truyền đúng Arguments và xử lý đúng quy trình được yêu cầu.

### 3.5. Quản lý Version Log và kết quả Evaluation

Một phần công việc khác mình phụ trách là cập nhật `artifacts/version_log.csv`.

Sau mỗi lần chạy Evaluation, mình lấy các thông tin từ Run JSON, bao gồm:

- `artifact_version`
- `prompt_hash`
- `tools_hash`
- `case_accuracy`
- `tool_routing_accuracy`
- `argument_accuracy`
- `multiturn_accuracy`
- `failure_counts`

Sau đó, mình ghi nhận những thông tin cần thiết vào Version Log để theo dõi các phiên bản.

**Kết quả đã ghi nhận:**

| Version | Metric Before | Metric After |
|---|---|---|
| v0 | N/A | 70% |
| v1 | 70% | 80% |
| v2 | 80% | 90% |
| v3 | 90% | 100% |

Mình cũng kiểm tra lại file CSV bằng PowerShell để đảm bảo các phiên bản được đọc đúng và không bị lỗi định dạng.

Theo mình, việc giữ lại Version Log và Run JSON khá hữu ích vì khi cần viết báo cáo hoặc giải thích một thay đổi, nhóm có thể quay lại xem kết quả thực tế thay vì phải nhớ từng lần chạy.

### 3.6. Kiểm tra Wikipedia Tool

Ngoài việc chạy Evaluation, mình cũng kiểm tra phần tích hợp Wikipedia Tool do Văn Trường phát triển.

Đầu tiên, mình kiểm tra sự tồn tại của hai file:

    tools/wikipedia/tool.py
    tools/wikipedia/TOOL.md

Cả hai file đều đã tồn tại.

Sau đó, mình kiểm tra `tools/__init__.py` và xác nhận Wikipedia Tool đã được import bằng hàm `wiki_search`, đồng thời được đăng ký với tên `wikipedia` trong `TOOL_FUNCTIONS`.

Mình cũng kiểm tra `tools.yaml` và xác nhận công cụ đã được khai báo.

Cuối cùng, mình chạy Tool Contract Tests:

    .\.venv\Scripts\python.exe -m pytest tests/test_tool_contract.py -q

**Kết quả:**

- **60 tests passed**
- **0 tests failed**

Kết quả này giúp mình xác nhận việc tích hợp Wikipedia Tool đã vượt qua các Tool Contract Tests có sẵn.

Tuy nhiên, kết quả trên không thay thế cho Unit Tests riêng của Wikipedia Tool. Những bài test kiểm tra dữ liệu đầu vào, kết quả trả về và các trường hợp lỗi vẫn cần được xác nhận riêng.

### 3.7. Phối hợp và theo dõi công việc nhóm

Trong quá trình thực hiện bài Lab, mình thường xuyên trao đổi với các thành viên về tiến độ và những vấn đề xuất hiện khi chạy Evaluation.

Khi một phiên bản có cases FAIL, mình gửi lại kết quả để thành viên phụ trách có thể xem nguyên nhân và điều chỉnh. Sau khi nhận bản cập nhật, mình tiếp tục chạy Evaluation để kiểm tra thay đổi có hiệu quả hay không.

Mình cũng kiểm tra phần tích hợp Wikipedia Tool và theo dõi các công việc liên quan đến Group Evaluation, UI và báo cáo nhóm.

Qua quá trình này, mình nhận thấy việc chia công việc giúp nhóm có thể thực hiện nhiều phần song song. Tuy nhiên, mọi người vẫn cần thống nhất thời điểm cập nhật code và chạy Evaluation, vì nếu nhiều file được thay đổi cùng lúc thì sẽ khó biết kết quả cải thiện đến từ đâu.

Đây cũng là một trong những điều mình rút kinh nghiệm khi đảm nhận vai trò nhóm trưởng.

### 3.8. Chạy Group Evaluation

Sau khi nhóm hoàn thành bộ test riêng trong `data/eval_group.json`, mình tiếp tục chạy Group Evaluation để kiểm tra Agent với những tình huống do nhóm tự thiết kế.

Lệnh mình sử dụng:

    python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json

Bộ Evaluation gồm 10 test cases, kiểm tra các tình huống như lựa chọn Wikipedia Tool, chuyển đổi giữa các công cụ, xử lý thông tin còn thiếu, hội thoại nhiều lượt và xác nhận trước khi gửi nội dung.

**Kết quả Group Evaluation:**

| Metric | Kết quả |
|---|---:|
| Total Cases | 10 |
| Measured Cases | 10 |
| Passed Cases | 10 |
| Case Accuracy | 100% |
| Tool Routing Accuracy | 100% |
| Argument Accuracy | 100% |
| Multiturn Accuracy | 100% |
| Provider Error Cases | 0 |

Mình cũng kiểm tra kết quả của từng case và xác nhận cả 10 cases đều PASS.

Kết quả này giúp mình có thêm bằng chứng về khả năng sử dụng Tool của Agent trên bộ kiểm thử do nhóm xây dựng. Tuy nhiên, đây vẫn là kết quả Evaluation, chưa thay thế cho việc kiểm thử chức năng thực tế khi các Tool kết nối với API bên ngoài.

## 4. Bằng chứng

### 4.1. Các file và kết quả thực hiện

**Version Log:**

`starter_v0/artifacts/version_log.csv`

**Run JSON của các phiên bản:**

- `starter_v0/runs/v0_B_base_openrouter_20261110T174407112036.json`
- `starter_v0/runs/v1_B_base_openrouter_20261110T180213807365.json`
- `starter_v0/runs/v2_B_base_openrouter_20261110T181404462799.json`
- `starter_v0/runs/v3_B_base_openrouter_20261111T002233736709.json`

**Các file liên quan đến việc kiểm tra tích hợp:**

- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/artifacts/tools.yaml`
- `starter_v0/tools/__init__.py`
- `starter_v0/tools/wikipedia/tool.py`
- `starter_v0/tools/wikipedia/TOOL.md`
- `starter_v0/tests/test_tool_contract.py`

**GitHub Repository:**

https://github.com/ArthurTheMana/K5-L3B-DAY03-Nhom4B-ResearchAgentToolEval

**Báo cáo cá nhân trên GitHub:**

https://github.com/ArthurTheMana/K5-L3B-DAY03-Nhom4B-ResearchAgentToolEval/blob/main/report/team/2A202603828_NguyenTaiMinhHuy.md

**Git Commit:** Bổ sung mã commit thực tế nếu cần đối chiếu lịch sử đóng góp.


### 4.2. AI và công cụ đã sử dụng

Trong bài Lab, mình có sử dụng ChatGPT để hỗ trợ tìm hiểu yêu cầu, giải thích lỗi và hướng dẫn thực hiện một số bước kỹ thuật.

Cụ thể, mình sử dụng ChatGPT để:

1. Đọc và giải thích yêu cầu trong README và các Checkpoints.
2. Hiểu những công việc mình cần thực hiện với vai trò nhóm trưởng.
3. Tìm cách xử lý lỗi Python và PowerShell khi thiết lập môi trường.
4. Giải thích lỗi API Key và Provider Preflight.
5. Hướng dẫn chạy `pytest` và `run_eval.py`.
6. Hỗ trợ phân tích kết quả Evaluation và những cases thất bại.
7. Hướng dẫn lấy Prompt Hash, Tools Hash và Artifact Version từ Run JSON.
8. Hỗ trợ tổng hợp số liệu và trình bày báo cáo bằng Markdown.

Mặc dù có sử dụng AI để hỗ trợ, mình vẫn trực tiếp chạy các lệnh trên máy, kiểm tra Terminal Output và đối chiếu kết quả với Run JSON.

Mình không sử dụng số liệu Accuracy do AI tự tạo mà dựa trên kết quả Evaluation thực tế của từng phiên bản.

Ngoài ra, mình không đưa API Key hoặc nội dung file `.env` vào báo cáo hay các bằng chứng được chia sẻ.

## 5. Tự đánh giá

Qua bài Lab Day 03 - Research Agent Tool Eval, mình hiểu rõ hơn cách một AI Agent sử dụng những công cụ bên ngoài thông qua Tool Calling, cũng như cách kiểm tra xem Agent có đang sử dụng những công cụ đó đúng hay không.

Ban đầu, mình nghĩ rằng chỉ cần Agent kết nối được với API và gọi được Tool là đã gần như hoàn thành. Tuy nhiên, sau khi chạy Evaluation, mình nhận ra rằng có khá nhiều vấn đề cần quan tâm, chẳng hạn như Agent có chọn đúng Tool không, Arguments có chính xác không, có biết hỏi lại khi thiếu thông tin hay không và có xử lý đúng những yêu cầu cần xác nhận trước khi thực hiện hay không.

Điều mình học được nhiều nhất là cách sử dụng **Evidence-driven Evaluation (đánh giá dựa trên bằng chứng)**. Thay vì chỉ nhìn vào câu trả lời của Agent rồi cho rằng nó hoạt động tốt, mình cần xem các test cases, đọc kết quả PASS/FAIL và kiểm tra cụ thể nguyên nhân của từng lỗi.

Khi chạy từ v0 đến v3, mình thấy rõ sự thay đổi của Agent qua từng phiên bản. Case Accuracy tăng từ 70% lên 80%, 90% và cuối cùng là 100%. Điều này giúp mình hiểu hơn về tác động của System Prompt và Tool Declaration đối với cách Agent lựa chọn công cụ và truyền tham số.

Tuy nhiên, mình cũng nhận ra rằng kết quả tốt trên bộ test cố định chưa chắc phản ánh đầy đủ chất lượng của một hệ thống thực tế. Một Agent có thể đạt 100% trong Evaluation nhưng vẫn cần được kiểm tra thêm với những câu hỏi mới, dữ liệu thật và các trường hợp lỗi khác nhau.

Về kỹ năng kỹ thuật, mình đã thực hành cách thiết lập Virtual Environment trên Windows, sử dụng pytest, kết nối OpenRouter API, đọc Run JSON và quản lý kết quả theo phiên bản.

Về kỹ năng làm việc nhóm, mình học được cách theo dõi tiến độ, trao đổi kết quả kiểm thử và phối hợp với các thành viên khi cần tích hợp những thay đổi vào cùng một hệ thống.

Mình nghĩ điểm mình cần cải thiện là khả năng tự đọc và phân tích Run JSON sâu hơn, cũng như chủ động thiết kế thêm những test cases mới thay vì chỉ sử dụng bộ Evaluation đã có sẵn. Ngoài ra, mình cũng muốn hiểu rõ hơn cách kiểm tra hoạt động của các Tool với API thật, vì việc chọn đúng Tool trong Evaluation chưa có nghĩa là dữ liệu thực tế luôn được lấy thành công.

**Kết luận:** Với vai trò nhóm trưởng, mình đã trực tiếp thực hiện việc thiết lập môi trường, kiểm tra Provider Preflight, chạy Baseline v0 và Evaluation v1-v3, cập nhật Version Log và kiểm tra Tool Contract của Wikipedia Tool. Qua những công việc này, mình hiểu rõ hơn quy trình kiểm thử và cải thiện AI Agent dựa trên kết quả thực tế, đồng thời có thêm kinh nghiệm trong việc phối hợp và quản lý công việc nhóm.
