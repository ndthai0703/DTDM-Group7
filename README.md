## 📌 Cấu trúc dự án

```
project_group7/
├── README.md                # Giới thiệu project và hướng dẫn chạy
│
├── model/                   # Quá trình huấn luyện & đánh giá mô hình AI
│   ├── README.md            # Nguồn dữ liệu, cách train và đánh giá
│   ├── requirements.txt     # Thư viện cho quá trình train
│   ├── preprocess.py        # Làm sạch, loại trùng, chia train/test
│   ├── train.py             # Huấn luyện và xuất model
│   ├── evaluate.py          # Đánh giá mô hình
│   ├── data/                # Chứa dữ liệu gốc (raw) và dữ liệu đã xử lý (processed)
│   ├── artifacts/           # Lưu trữ model thật (sentiment-v1.json)
│   └── results/             # Kết quả đánh giá (metrics.json, confusion_matrix.png)
│
├── lambda/                  # Mã nguồn suy luận chạy trên AWS Lambda
│   ├── README.md 
│   ├── lambda_function.py   # Handler nạp model ngoài phạm vi hàm, suy luận & ghi DynamoDB
│   ├── requirements.txt     # Thư viện cần thiết cho môi trường Lambda
│   ├── Dockerfile           # File cấu hình build Docker Image cho Lambda
│   ├── .dockerignore        # Các tệp/thư mục loại trừ khi build Docker image
│   ├── create_demo_model.py # Tạo model giả lập phục vụ chạy thử local
│   ├── model.json           # Model demo dùng cho môi trường thử nghiệm
│   ├── test_local.py        # Kịch bản test hàm Lambda Handler trực tiếp bằng Python
│   └── events/              # Tệp cấu hình sự kiện đầu vào mẫu (valid/invalid)
│
├── frontend/                # Giao diện người dùng
│   ├── README.md
│   └── index.html           # Trang giao diện chính
│
├── infra/                   # Cấu hình hạ tầng trên AWS
│   ├── README.md
│   └── config.example.json  # Tệp cấu hình tham số hạ tầng mẫu
│
├── loadtest/                # Kiểm thử tải hệ thống bằng Locust
│   ├── README.md            # Hướng dẫn chạy, thời lượng và mức tải
│   ├── requirements.txt     # Thư viện phục vụ load test
│   ├── locustfile.py        # Kịch bản mô phỏng request gửi tới API
│   └── results/             # Báo cáo kết quả kiểm thử (10_users, 50_users, 100_users)
│
├── tests/                   # Kiểm tra chức năng và tích hợp hệ thống
│   ├── README.md            # Hướng dẫn chi tiết cách chạy kiểm thử
│   ├── test_inference.py    # Unit test kiểm tra độ chính xác của logic suy luận
│   └── test_api.py          # Integration test API thực tế và xử lý ngoại lệ
│
├── scripts/                 # Bộ công cụ hỗ trợ tự động hóa và triển khai
│   ├── README.md            # Hướng dẫn chi tiết các tham số dòng lệnh
│   ├── run_local.py         # Giả lập môi trường Web & API chạy trực tiếp trên máy
│   ├── upload_model.py      # Tải model artifact lên bộ lưu trữ Amazon S3
│   ├── build_and_push.ps1   # Script tự động Build & Push Docker image lên AWS ECR
│   ├── deploy_lambda.py     # Script khởi tạo/cập nhật hàm AWS Lambda từ ECR Image
│   ├── upload_frontend.py   # Tải tài nguyên giao diện lên S3 Static Website
│   └── check_quota.py       # Kiểm tra hạn ngạch Concurrency của tài khoản AWS
│
└── docs/                    # Tài liệu tổng hợp, thiết kế và minh chứng hệ thống
    ├── demo-guide.md        # Hướng dẫn kịch bản demo chi tiết
    ├── task-tracking.md     # Bảng phân công công việc và tiến độ
    ├── diagrams/            # Sơ đồ kiến trúc hạ tầng và luồng dữ liệu
    ├── report/              # Báo cáo tổng kết dự án
    ├── slides/              # Slide thuyết trình
    └── evidence/            # Ảnh minh chứng thực tế trên console AWS (ECR, DynamoDB, CloudWatch, Billing...)
