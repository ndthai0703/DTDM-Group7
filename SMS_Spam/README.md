# – SMS Spam / Ham + AWS Load Test

## Trạng thái
Bài toán nhóm chốt: **phân loại tin nhắn SMS thành `spam` hoặc `ham`**. Bộ này thay thế Iris `.joblib` trước đây. Model `spam-v1.json` là model Multinomial Naive Bayes (bag-of-words) xuất JSON, chạy suy luận bằng Python chuẩn, không cần scikit-learn trong Lambda.

## Chạy trong VS Code / Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python train_model.py
python predict_local.py "Congratulations! You won free money, claim now"
python predict_local.py "Please send me the lecture notes tomorrow"
```

## Dataset chuẩn cho đánh giá học thuật
Khuyến nghị tải **UCI SMS Spam Collection (5.574 tin, nhãn ham/spam, tiếng Anh)** từ https://archive.ics.uci.edu/dataset/228/sms+spam+collection. Chuyển thành CSV với cột `label,text`, chạy `python train_model.py --data data/uci_sms.csv`, gửi lại file `spam-v1.json` và `results/local_metrics.json`. Các metric demo phải được thay bằng metric UCI sau khi chạy. Không dùng test set để huấn luyện.

## JSON hợp đồng API
**Request** `POST /predict`:
```json
{"text":"Congratulations! You won free cash. Claim now!"}
```
**Response ví dụ hình thức** (không phải số đo AWS):
```json
{"label":"spam","confidence":0.97,"processing_time_ms":4.2,"model_version":"spam-v1"}
```
Nhãn chỉ nhận `spam` hoặc `ham`, `confidence` từ 0 đến 1. Trường `processing_time_ms` phải đo trong Lambda. Lỗi input trả HTTP 400. Code demo trong `lambda_reference.py` chỉ để tham khảo và **chưa có DynamoDB**.

### Cấu trúc `spam-v1.json`
- `schema_version`, `model_version`, `task`, `algorithm`, `labels`
- `tokenizer.pattern` (regex), `class_log_prior` (log xác suất tiên nghiệm)
- `feature_log_prob.ham`, `feature_log_prob.spam`: log xác suất có điều kiện theo từ
- `unknown_log_prob`: trọng số từ mới chưa gặp trong train

Trọng số lưu dạng log để tính ổn định. `predict_local.py` phải đi cùng file JSON trong image Lambda. Nếu Lambda cũ chỉ đọc sentiment JSON kiểu `positive/negative`, Thái phải thay parser và output theo schema mới; không thể chỉ rename file.

## Kiểm thử tải Locust (AWS thật – CHƯA CHẠY)
Sau khi gửi URL API, xác nhận Lambda concurrency và ngân sách AWS, kiểm tra bằng 1 request trước. Chú ý API_PATH mặc định `/predict` (có thể đặt biến môi trường). Nếu stage nằm sau hostname, dùng `--host` có stage tương ứng.

```powershell
python -m locust -f locustfile.py --headless --host https://API_ID.execute-api.ap-southeast-1.amazonaws.com --users 10 --spawn-rate 2 --run-time 2m --csv results/aws_10
python -m locust -f locustfile.py --headless --host https://API_ID.execute-api.ap-southeast-1.amazonaws.com --users 50 --spawn-rate 5 --run-time 2m --csv results/aws_50
python -m locust -f locustfile.py --headless --host https://API_ID.execute-api.ap-southeast-1.amazonaws.com --users 100 --spawn-rate 10 --run-time 2m --csv results/aws_100
```

Hoặc `python run_loadtest.py --host https://... --confirm-aws` . Xuất CSV, ghi P50/P95, RPS, số request, HTTP 429/5xx, Lambda ConcurrentExecutions, Throttles, Duration P95 và ảnh CloudWatch. **100 users Locust không có nghĩa là 100 Lambda chạy đồng thời.**