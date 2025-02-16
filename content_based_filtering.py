from flask import Flask, request, jsonify
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df_user = pd.read_csv("data/user_rcp.csv")
df_class = pd.read_csv("data/class_rcp.csv")

# Gabungkan interests dan tags
combined_data = pd.concat([df_user["interests"], df_class["tags"]])

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(combined_data)

# Pisahkan vektor pengguna dan kursus
user_vectors = tfidf_matrix[: len(df_user)]
course_vectors = tfidf_matrix[len(df_user) :]

# Hitung Cosine Similarity
similarity_scores = cosine_similarity(user_vectors, course_vectors)

app = Flask(__name__)


@app.route("/recommend", methods=["POST"])
def recommend():
    user_id = request.json["user_id"]
    user_idx = df_user[df_user["id"] == user_id].index[0]
    similar_courses_idx = similarity_scores[user_idx].argsort()[::-1]
    recommended_courses = df_class.iloc[similar_courses_idx[:3]].to_dict(
        orient="records"
    )
    return jsonify(recommended_courses)


if __name__ == "__main__":
    app.run(debug=True)
