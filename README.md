---
title: Shopee Sentiment Analysis
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: streamlit
app_file: app.py
pinned: false
license: mit
sdk_version: 1.56.0
---

# Shopee Sentiment Analysis

Ứng dụng này dùng Streamlit để phân tích cảm xúc từ review Shopee.

## Tính năng
- Dự đoán cảm xúc cho từng review nhập tay.
- Phân tích hàng loạt từ file CSV với các cột như `comment`, `review_text`, `review`, `content`, `text`.
- Phân tích trực tiếp từ link sản phẩm Shopee để lấy review và thống kê cảm xúc.

## Cách chạy
- Hugging Face sẽ tự động chạy `app.py` bằng SDK Streamlit.
- Các thư viện cần thiết được cài đặt từ `requirements.txt`.

## Huấn luyện lại mô hình
- Người dùng có thể fork Space này và chỉnh sửa code trong thư mục `src/` để huấn luyện lại mô hình.
- Bạn có thể thay đổi dữ liệu hoặc thuật toán trong `predict.py` và `preprocess.py`.

## Thông tin thêm
- License: MIT (cho phép sử dụng và chỉnh sửa tự do, chỉ cần giữ nguyên thông tin bản quyền).
