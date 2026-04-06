import pandas as pd
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# đọc file dữ liệu
file_path = os.path.join(BASE_DIR, "data", "processed_reviews.csv")
df = pd.read_csv(file_path)

# lấy feature và label
X = df["clean_comment"]
y = df["sentiment_label"]

# vector hóa text
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2)
)
X_vec = vectorizer.fit_transform(X)

# chia train test
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

# train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# đánh giá
y_pred = model.predict(X_test)
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# lưu model
model_dir = os.path.join(BASE_DIR, "model")
os.makedirs(model_dir, exist_ok=True)

with open(os.path.join(model_dir, "model.pkl"), "wb") as f:
    pickle.dump(model, f)

with open(os.path.join(model_dir, "vectorizer.pkl"), "wb") as f:
    pickle.dump(vectorizer, f)

print("🎉 Đã lưu model thành công!")