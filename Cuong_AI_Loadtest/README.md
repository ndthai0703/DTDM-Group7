# Cường — AI model và load test (bản mẫu chạy được)

**Lưu ý:**Bộ Iris và Logistic Regression là phương án đề xuất, cần xác nhận trước khi tích hợp. Không có số liệu AWS thực tế trong bộ này.

## Chạy local

```bash
python -m pip install -r requirements.txt
python train_model.py
python predict_local.py
```

`train_model.py` xuất `iris_model.joblib` và `metrics.json`. Lambda có thể tải file từ S3 hoặc đóng gói vào container; phải giữ phiên bản thư viện tương thích.

## Hợp đồng API đề xuất

POST `/predict` với JSON:

```json
{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}
```

Response (giá trị ví dụ, không phải kết quả AWS):

```json
{"label":"setosa","confidence":0.98,"processing_time_ms":12.4}
```

`processing_time_ms` do Lambda đo và trả về. Nhãn có thể là `setosa`, `versicolor`, `virginica`.

## Chạy kiểm thử tải với API thật

Chỉ chạy sau khi cung cấp URL và đồng ý giới hạn chi phí/concurrency. Nếu API có stage prefix (ví dụ `/prod`), thêm stage vào `--host`.

```bash
locust -f locustfile.py --headless --host https://YOUR_API_ID.execute-api.ap-southeast-1.amazonaws.com --users 10 --spawn-rate 2 --run-time 2m --csv run10
locust -f locustfile.py --headless --host https://YOUR_API_ID.execute-api.ap-southeast-1.amazonaws.com --users 50 --spawn-rate 5 --run-time 2m --csv run50
locust -f locustfile.py --headless --host https://YOUR_API_ID.execute-api.ap-southeast-1.amazonaws.com --users 100 --spawn-rate 10 --run-time 2m --csv run100
```

**Chú ý:** 100 người dùng mô phỏng không có nghĩa là 100 Lambda chạy đồng thời. Ghi lại requests/s, số request, lỗi, P50/P95, HTTP 429, ConcurrentExecutions, Throttles và Duration P95 trên CloudWatch. Nếu reserved concurrency là 20, các mức tải cao có thể bị throttling. Không tăng quota hay tải khi chưa có sự đồng ý của nhóm.
