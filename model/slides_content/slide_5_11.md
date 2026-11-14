# Mô hình AI 
- Bài toán: phân loại SMS thành **spam** (rác) / **ham** (hợp lệ).
- Pipeline: nhãn + văn bản -> tokenizer -> Multinomial Naive Bayes -> xuất `spam-v1.json`.
- Input API: `{"text":"..."}`; output: `label`, `confidence`, `processing_time_ms`.
- Chèn accuracy, precision/recall/F1 từ kết quả UCI chính thức; không lấy metric demo để khẳng định hiệu năng thực tế.

# Kiểm thử tải 
- Locust: 10 / 50 / 100 người dùng, thời lượng 2 phút/mức; chỉ chạy khi nhóm duyệt.
- Ghi số request, RPS, lỗi HTTP 429/5xx, latency P50/P95.
- Đối chiếu CloudWatch: Lambda ConcurrentExecutions, Throttles, Duration P95, Invocations.
- Đưa CSV, bảng số liệu và ảnh AWS **sau khi chạy**. Trước thời điểm đó ghi "chưa thử nghiệm thực tế".
