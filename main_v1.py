import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from flask import Flask, request, jsonify
import numpy as np

# Load user, class, and user-class interaction data
df_user = pd.read_json("data/json/users_generated.json")
df_class = pd.read_json("data/json/classes.json")
df_user_class = pd.read_json("data/json/users_classes_generated.json")


# Ensure all fields are present and handle missing values appropriately
def preprocess_data(df_user, df_class):
    # Handle missing 'interests' and 'tags'
    df_user["interests"] = df_user.get("interests", []).apply(
        lambda x: x if isinstance(x, list) else []
    )
    df_class["tags"] = df_class.get("tags", []).apply(
        lambda x: x if isinstance(x, list) else []
    )

    # Flatten lists of strings into single strings
    flatten_list = lambda lst: " ".join(
        [
            str(item)
            for sublist in lst
            for item in (sublist if isinstance(sublist, list) else [sublist])
        ]
    )

    user_interests = df_user["interests"].apply(flatten_list)
    class_tags = df_class["tags"].apply(flatten_list)

    return user_interests, class_tags


user_interests, class_tags = preprocess_data(df_user, df_class)
combined_data = pd.concat([user_interests, class_tags], ignore_index=True)

# Initialize TF-IDF Vectorizer with optimized parameters
vectorizer = TfidfVectorizer(
    stop_words="english", ngram_range=(1, 2), max_features=5000
)

# Apply TF-IDF vectorizer
tfidf_matrix = vectorizer.fit_transform(combined_data)

# Separate user vectors and course vectors
num_users = len(df_user)
user_vectors = tfidf_matrix[:num_users]  # Users' interests
course_vectors = tfidf_matrix[num_users:]  # Courses' tags

# Compute cosine similarity between users and courses
cosine_sim = cosine_similarity(user_vectors, course_vectors)

# Create user-item matrix
user_course_matrix = pd.pivot_table(
    df_user_class, values="rating", index="user_id", columns="class_id"
)

# Fill missing values with 0 (implicit feedback: no interaction = 0 rating)
user_course_matrix = user_course_matrix.fillna(0)

# Apply SVD for matrix factorization with n_components <= number of features
svd = TruncatedSVD(
    n_components=10, random_state=42
)  # Adjust the number of components here
svd_matrix = svd.fit_transform(user_course_matrix)


# Compute predicted ratings by reconstructing the matrix
predicted_ratings = np.dot(svd_matrix, svd.components_)


# Hybrid Recommendation: Combine content-based and collaborative filtering scores
def get_hybrid_recommendation(user_id, top_n=3):
    try:
        # Find the user index
        user_idx = df_user[df_user["id"] == user_id].index[0]
    except IndexError:
        print(f"User ID {user_id} not found.")
        return [], {}

    # Get content-based similarity scores for the user
    content_scores = cosine_sim[user_idx]
    # Get collaborative filtering predicted ratings for the user
    collab_scores = predicted_ratings[user_idx]

    # Normalize content-based scores
    content_scaler = MinMaxScaler()
    content_scores_norm = content_scaler.fit_transform(
        content_scores.reshape(-1, 1)
    ).flatten()

    # Normalize collaborative filtering scores
    collab_scaler = MinMaxScaler()
    collab_scores_norm = collab_scaler.fit_transform(
        collab_scores.reshape(-1, 1)
    ).flatten()

    def softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    content_scores_norm = softmax(content_scores)
    collab_scores_norm = softmax(collab_scores)
    hybrid_scores = (0.8 * content_scores_norm) + (0.2 * collab_scores_norm)

    # Apply a small popularity boost (e.g., 10%)
    course_popularity = df_user_class.groupby("class_id")["rating"].mean()
    popularity_scores = course_popularity / course_popularity.max()
    hybrid_scores += 0.1 * popularity_scores.values

    # Get top N course recommendations based on the hybrid scores
    recommended_idx = hybrid_scores.argsort()[::-1][:top_n]
    recommended_courses = df_class.iloc[recommended_idx].to_dict(orient="records")

    # Metrics Calculation
    user_actual_courses = df_user_class[
        (df_user_class["user_id"] == user_id) & (df_user_class["rating"] >= 4)
    ]["class_id"].tolist()
    recommended_course_ids = df_class.iloc[recommended_idx]["id"].tolist()
    true_positives = len(set(recommended_course_ids) & set(user_actual_courses))

    precision = (
        true_positives / len(recommended_course_ids) if recommended_course_ids else 0
    )
    recall = true_positives / len(user_actual_courses) if user_actual_courses else 0
    f1_score = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )
    coverage = (
        len(set(recommended_course_ids)) / len(df_class) if len(df_class) > 0 else 0
    )

    metrics = {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1_score, 2),
        "coverage": round(coverage, 2),
    }
    return recommended_courses, metrics


# app = Flask(__name__)


# @app.route("/recommend", methods=["GET"])
# def recommend():
#     user_id = request.json["user_id"]  # Get user ID from request

#     # Get the top 3 recommended courses using the hybrid model
#     recommended_courses, metrics = get_hybrid_recommendation(user_id, top_n=5)

#     return jsonify({"recommended_courses": recommended_courses, "metrics": metrics})


# if __name__ == "__main__":
#     app.run(debug=True)

precision = 0
recall = 0
f1_score = 0
coverage = 0

for i in range(1, 11):
    _, metrics = get_hybrid_recommendation(i, top_n=3)
    precision += metrics["precision"]
    recall += metrics["recall"]
    f1_score += metrics["f1_score"]
    coverage += metrics["coverage"]

average_precision = precision / 10
average_recall = recall / 10
average_f1_score = f1_score / 10
average_coverage = coverage / 10

print(
    f"Average Precision: {average_precision}\nAverage Recall: {average_recall}\nAverage F1-Score: {average_f1_score}\nAverage Coverage: {average_coverage}"
)

# recommendation, metrics = get_hybrid_recommendation(9, top_n=5)
# print("Recommended Courses:", recommendation)
# print("Metrics:", metrics)
