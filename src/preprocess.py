import re
from underthesea import word_tokenize
import pandas as pd
import os
teencode_dict = {
    "ko": "không",
    "k": "không",
    "khong": "không",
    "không": "không",
    "dc": "được",
    "đc": "được",
    "được": "được",
    "ko biết": "không biết",
    "kg": "không",
    "khg": "không",
    "không biết": "không biết",
    "k biết": "không biết",
    "k bt": "không biết",
    "k biết đâu": "không biết đâu",
    "j": "gì",
    "vè": "về",
    "v": "và",
    "vs": "với",
    "ok": "ok", "okie": "ok", "okey": "ok", "okela": "ok", "okê": "ok", "okay": "ok",
    "iu": "yêu", "shipper": "người giao hàng", "shop": "cửa hàng",
}
def clean_text(text):
    if not isinstance(text, str):
        return ""

    #1.Chuyển về chữ thường
    text = text.lower()
    
    #2 Xóa các kí tự đặc biệt, icon, linkweb
    text = re.sub(r"https\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s]', ' ', text)
    #3. sửa teencode
    words = text.split()
    words = [teencode_dict.get(word, word) for word in words]
    text = ' '.join(words)
    
    #4. Tách từ tiếng việt
    text = word_tokenize(text, format="text")
    return text


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(BASE_DIR, "data", "shopee_reviews_2000_realistic.csv")

    df = pd.read_csv(file_path)

    # tạo cột text sạch
    df["clean_comment"] = df["review_text"].apply(clean_text)

    # lưu file mới
    output_path = os.path.join(BASE_DIR, "data", "processed_reviews.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("✅ Đã preprocess xong!")
    print(df[["review_text", "clean_comment"]].head())

