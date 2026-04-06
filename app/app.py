import streamlit as st
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from src.predict import predict_sentiment

st.set_page_config(
    page_title="Shopee Sentiment AI",
    page_icon="🛍️",
    layout="centered"
)

st.title("🛍️ Shopee Review Sentiment Analysis")
st.markdown("### 🤖 AI phân tích cảm xúc đánh giá sản phẩm")

review = st.text_area(
    "✍️ Nhập review sản phẩm:",
    placeholder="Ví dụ: shop giao hàng nhanh, chất lượng rất tốt"
)

if st.button("🚀 Dự đoán"):
    if review.strip():
        result = predict_sentiment(review)

        if "Positive" in result:
            st.success(result)
        elif "Negative" in result:
            st.error(result)
        else:
            st.warning(result)
    else:
        st.warning("⚠️ Vui lòng nhập review")