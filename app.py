import re
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.predict import predict_sentiment
from src.shopee_reviews import ShopeeReviewError, fetch_product_reviews


st.set_page_config(
    page_title="Shopee Sentiment AI",
    page_icon="🛍️",
    layout="centered",
)

st.title("🛍️ Shopee Review Sentiment Analysis")
st.markdown("### 🤖 AI phân tích cảm xúc + tìm lý do")

positive_keywords = [
    "tốt",
    "đẹp",
    "xịn",
    "ổn",
    "ok",
    "ưng",
    "nhanh",
    "chất lượng",
    "hài lòng",
]

negative_keywords = [
    "chậm",
    "lỗi",
    "tệ",
    "kém",
    "hỏng",
    "vỡ",
    "fake",
    "không",
    "xấu",
]

COMMENT_COLUMNS = ("comment", "review_text", "review", "content", "text")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_ngrams(text, n=2):
    words = text.split()
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def extract_reasons(comments, sentiment_type):
    all_words = []
    all_bigrams = []

    for comment in comments:
        text = clean_text(comment)
        words = text.split()
        bigrams = get_ngrams(text, 2)
        all_words.extend(words)
        all_bigrams.extend(bigrams)

    word_counter = Counter(all_words)
    bigram_counter = Counter(all_bigrams)
    keywords = positive_keywords if sentiment_type == "Positive" else negative_keywords

    keyword_hits = {keyword: word_counter[keyword] for keyword in keywords if keyword in word_counter}
    top_bigrams = bigram_counter.most_common(5)
    results = sorted(keyword_hits.items(), key=lambda item: item[1], reverse=True)[:5]

    return results, top_bigrams


def find_comment_column(dataframe):
    normalized_columns = {str(column).strip().lower(): column for column in dataframe.columns}
    for candidate in COMMENT_COLUMNS:
        if candidate in normalized_columns:
            return normalized_columns[candidate]
    raise ValueError(
        "File CSV phai co mot trong cac cot: "
        + ", ".join(COMMENT_COLUMNS)
    )


def extract_comments(dataframe):
    comment_column = find_comment_column(dataframe)
    comments = (
        dataframe[comment_column]
        .dropna()
        .astype(str)
        .map(str.strip)
    )
    comments = [comment for comment in comments if comment]
    return comment_column, comments


def analyze_comments(comments):
    stats = {"Positive": 0, "Negative": 0, "Neutral": 0}
    positive_comments = []
    negative_comments = []
    neutral_comments = []

    for comment in comments:
        result = predict_sentiment(comment)

        if "Positive" in result:
            stats["Positive"] += 1
            positive_comments.append(comment)
        elif "Negative" in result:
            stats["Negative"] += 1
            negative_comments.append(comment)
        else:
            stats["Neutral"] += 1
            neutral_comments.append(comment)

    return stats, positive_comments, negative_comments, neutral_comments


def render_analysis(comments):
    stats, positive_comments, negative_comments, _ = analyze_comments(comments)
    total = sum(stats.values())

    if total == 0:
        st.warning("⚠️ Không có dữ liệu hợp lệ để phân tích")
        return

    percentages = {label: round(count / total * 100, 2) for label, count in stats.items()}

    col1, col2, col3 = st.columns(3)
    col1.metric("😊 Positive", stats["Positive"], f"{percentages['Positive']}%")
    col2.metric("😐 Neutral", stats["Neutral"], f"{percentages['Neutral']}%")
    col3.metric("😡 Negative", stats["Negative"], f"{percentages['Negative']}%")

    fig, ax = plt.subplots()
    ax.pie(
        percentages.values(),
        labels=percentages.keys(),
        autopct="%1.1f%%",
        startangle=90,
        colors=["#4CAF50", "#FFC107", "#F44336"],
        wedgeprops={"edgecolor": "white"},
    )
    ax.set_title("📊 Tỷ lệ cảm xúc bình luận")
    st.pyplot(fig)
    plt.close(fig)

    star_score = (
        stats["Positive"] * 5
        + stats["Neutral"] * 3
        + stats["Negative"] * 1
    ) / total

    st.subheader("⭐ Đánh giá tổng quan")
    st.write(f"{star_score:.1f} sao")

    full_stars = int(star_score)
    half_star = star_score - full_stars >= 0.5
    st.write("⭐" * full_stars + ("✨" if half_star else ""))

    st.subheader("🔍 Lý do phổ biến")
    pos_words, pos_bigrams = extract_reasons(positive_comments, "Positive")
    neg_words, neg_bigrams = extract_reasons(negative_comments, "Negative")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 😊 Positive")
        st.write("**Keyword:**")
        for word, count in pos_words:
            st.write(f"- {word} ({count})")
        st.write("**Cụm từ phổ biến:**")
        for word, count in pos_bigrams:
            st.write(f"- {word} ({count})")

    with col2:
        st.markdown("### 😡 Negative")
        st.write("**Keyword:**")
        for word, count in neg_words:
            st.write(f"- {word} ({count})")
        st.write("**Cụm từ phổ biến:**")
        for word, count in neg_bigrams:
            st.write(f"- {word} ({count})")


@st.cache_data(show_spinner=False)
def load_product_reviews(product_url, max_reviews):
    return fetch_product_reviews(product_url, max_reviews=max_reviews)


review = st.text_area(
    "✍️ Nhập review sản phẩm:",
    placeholder="Ví dụ: shop giao hàng nhanh, chất lượng rất tốt",
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
csv_tab, link_tab = st.tabs(["📂 Tải file CSV", "🔗 Dán link sản phẩm"])

with csv_tab:
    uploaded_file = st.file_uploader("📂 Tải lên file CSV chứa bình luận", type=["csv"])

    if uploaded_file:
        dataframe = pd.read_csv(uploaded_file)
        st.write("📄 Dữ liệu mẫu:", dataframe.head())

        try:
            comment_column, comments = extract_comments(dataframe)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.caption(f"Đang phân tích {len(comments)} bình luận từ cột `{comment_column}`.")
            render_analysis(comments)

with link_tab:
    product_url = st.text_input(
        "🔗 Dán link sản phẩm Shopee",
        placeholder="Ví dụ: https://shopee.vn/...-i.123456.7891011",
    )
    max_reviews = st.slider("📥 Số lượng bình luận tối đa", 20, 200, 100, 20)
    st.caption("Hỗ trợ link dạng `...-i.shopid.itemid`, `/product/shopid/itemid` hoặc short link Shopee.")

    if st.button("🔎 Phân tích từ link"):
        if not product_url.strip():
            st.warning("⚠️ Vui lòng nhập link sản phẩm Shopee")
        else:
            with st.spinner("Đang lấy bình luận từ Shopee..."):
                try:
                    dataframe = load_product_reviews(product_url.strip(), max_reviews)
                except ShopeeReviewError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Không thể lấy dữ liệu từ link sản phẩm. Hãy thử lại sau.")
                else:
                    preview_columns = [
                        column
                        for column in ("author_username", "rating_star", "comment")
                        if column in dataframe.columns
                    ]
                    st.success(f"Đã lấy {len(dataframe)} bình luận có nội dung từ sản phẩm.")
                    st.write("📄 Dữ liệu mẫu:", dataframe[preview_columns].head())
                    render_analysis(dataframe["comment"].tolist())
