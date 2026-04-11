import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

st.header("📊 Thống kê cảm xúc bình luận Shopee")

uploaded_file = st.file_uploader("📂 Tải lên file CSV chứa bình luận", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📄 Dữ liệu mẫu:", df.head())

    stats = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for review in df["comment"].dropna():
        result = predict_sentiment(review)
        if "Positive" in result:
            stats["Positive"] += 1
        elif "Negative" in result:
            stats["Negative"] += 1
        else:
            stats["Neutral"] += 1

    total = sum(stats.values())
    if total > 0:
        percentages = {k: round(v/total*100, 2) for k, v in stats.items()}

        col1, col2, col3 = st.columns(3)
        col1.metric("😊 Positive", stats["Positive"], f"{percentages['Positive']}%")
        col2.metric("😐 Neutral", stats["Neutral"], f"{percentages['Neutral']}%")
        col3.metric("😡 Negative", stats["Negative"], f"{percentages['Negative']}%")

        fig, ax = plt.subplots()
        colors = ['#4CAF50', '#FFC107', '#F44336']  # xanh lá, vàng, đỏ
        ax.pie(
            percentages.values(),
            labels=percentages.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops={'edgecolor':'white'}
        )
        ax.set_title("📊 Tỷ lệ cảm xúc bình luận", fontsize=14, fontweight='bold')
        st.pyplot(fig)

        star_score = (
            stats["Positive"]*5 +
            stats["Neutral"]*3 +
            stats["Negative"]*1
        ) / total

        st.subheader("⭐ Đánh giá tổng quan")
        st.write(f"Bình luận đánh giá trung bình: {star_score:.1f} sao")

        # Hiển thị sao trực quan
        full_stars = int(star_score)
        half_star = star_score - full_stars >= 0.5
        stars_display = "⭐" * full_stars + ("✨" if half_star else "")
        st.write(stars_display)
    else:
        st.warning("⚠️ File CSV không có dữ liệu hợp lệ trong cột 'comment'")
