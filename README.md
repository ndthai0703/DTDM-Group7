# Cấu trúc toàn bộ project

project_group7/
├── README.md # Giới thiệu project và hướng dẫn chạy
│
├── model/  # dữ liệu và mô hình AI
│   ├── README.md # Nguồn dữ liệu, cách train và đánh giá
│   ├── requirements.txt # Thư viện cho quá trình train
│   ├── preprocess.py # Làm sạch, loại trùng, chia train/test
│   ├── train.py  # Huấn luyện và xuất model
│   ├── evaluate.py  # Đánh giá 
│   ├── data/
│   │   ├── raw/ # Dữ liệu gốc
│   │   └── processed/ # Dữ liệu đã xử lý
│   ├── artifacts/
│   │   └── sentiment-v1.json # Model thật để upload lên S3
│   └── results/ # Các chỉ số đánh giá model
│       ├── metrics.json
│       └── confusion_matrix.png
│
├── lambda/ # Chạy suy luận trên Lambda
│   ├── README.md 
│   ├── lambda_function.py # Nạp model ngoài handler, suy luận, ghi DynamoDB và trả kết quả
│   ├── requirements.txt # Thư viện cần khi chạy Lambda
│   ├── Dockerfile # Hướng dẫn build Docker image
│   ├── .dockerignore # Loại file không cần khỏi build context
│   ├── create_demo_model.py # Tạo model tạm để thử local
│   ├── model.json  # Model demo
│   ├── test_local.py # Test handler bằng Python
│   └── events/
│       ├── valid.json # Test event có đầu vào hợp lệ
│       └── invalid.json # Test event có đầu vào sai
│
├── frontend/ # Giao diện người dùng
│   ├── README.md
│   └── index.html
│
├── infra/  # Cấu hình hạ tầng AWS
│   ├── README.md
│   ├── config.example.json
│
├── loadtest/ # kiểm thử
│   ├── README.md # Cách chạy, thời lượng và mức tải
│   ├── requirements.txt # Thư viện kiểm thử tải
│   ├── locustfile.py # Kịch bản gửi request tới API
│   └── results/ # Kết quả 
│       ├── 10_users/
│       ├── 50_users/
│       └── 100_users/
│
├── tests/   # Kiểm tra chức năng và tích hợp
│   ├── README.md # Hướng dẫn chạy test
│   ├── test_inference.py # Kiểm tra kết quả suy luận của model
│   └── test_api.py # Kiểm tra API thật và các trường hợp lỗi
│
├── scripts/ # Script hỗ trợ chạy và triển khai
│   ├── README.md # Cách dùng và tham số của các script
│   ├── run_local.py  # Chạy web và API giả lập trên máy
│   ├── upload_model.py # Upload model thật lên S3
│   ├── build_and_push.ps1 # Build/push image bằng PowerShell
│   ├── deploy_lambda.py # Tạo/cập nhật Lambda từ image ECR
│   ├── upload_frontend.py # Upload web lên S3
│   └── check_quota.py # Đọc quota concurrency của tài khoản
│
└── docs/ 
    ├── demo-guide.md
    ├── task-tracking.md
    ├── diagrams/
    ├── report/ 
    ├── slides/
    └── evidence/ # Ảnh minh chứng từ hệ thống thực tế
        ├── lambda_ecr/
        ├── api_dynamodb/
        ├── cloudwatch/
        ├── alarms/
        └── billing/
