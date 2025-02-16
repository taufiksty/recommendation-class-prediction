import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds

# Load your data
users = pd.read_json("data/json/users_generated.json")
classes = pd.read_json("data/json/classes.json")
users_classes = pd.read_json("data/json/users_classes_generated.json")


# 1. CBF
def content_based_filtering(user_id):
    user = users[users["id"] == user_id].iloc[0]
    user_interests = ",".join(user["interests"])
    print(type(user_interests))
    print(user_interests)

    classes_tags = classes["tags"].apply(
        lambda x: x if isinstance(x, str) else ",".join(x)
    )
    print(classes_tags)

    # TF-IDF Vectorization
    tfidf = TfidfVectorizer(stop_words="english")
    class_features = tfidf.fit_transform(classes_tags)
    user_vector = tfidf.transform([user_interests])

    # Calculate cosine similarity
    similarity = cosine_similarity(user_vector, class_features).flatten()

    # Normalize scores
    similarity_normalized = (similarity - similarity.min()) / (
        similarity.max() - similarity.min()
    )
    return similarity_normalized


# 2. CF
def collaborative_filtering(user_id):
    # User-Class interaction matrix
    interactions = users_classes.pivot(
        index="user_id", columns="class_id", values="rating"
    ).fillna(0)

    # Matrix factorization using SVD
    user_ratings = interactions.values
    user_means = np.mean(user_ratings, axis=1)
    user_ratings_demeaned = user_ratings - user_means.reshape(-1, 1)

    U, sigma, Vt = svds(user_ratings_demeaned, k=20)
    sigma = np.diag(sigma)

    # Predicted ratings
    predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_means.reshape(-1, 1)
    predictions_df = pd.DataFrame(
        predicted_ratings, columns=interactions.columns, index=interactions.index
    )

    if user_id in predictions_df.index:
        predictions = predictions_df.loc[user_id].values
    else:
        predictions = np.zeros(classes.shape[0])  # If user has no interactions

    # Normalize scores
    predictions_normalized = (predictions - predictions.min()) / (
        predictions.max() - predictions.min()
    )
    return predictions_normalized


# 3. Hybrid
def hybrid_recommendation(
    user_id,
    content_weight=0.5,
    collab_weight=0.5,
    top_n=len(classes),
    for_metrics=False,
):
    # Get scores from both models
    content_scores = content_based_filtering(user_id)
    collaborative_scores = collaborative_filtering(user_id)

    # Combine scores using weighted average
    hybrid_scores = (content_weight * content_scores) + (
        collab_weight * collaborative_scores
    )

    # Get top N recommendations
    recommendations = classes.copy()
    recommendations["score"] = hybrid_scores
    recommendations = recommendations.sort_values("score", ascending=False)

    taken_classes = users_classes[users_classes["user_id"] == user_id][
        "class_id"
    ].tolist()

    recommendations = recommendations[~recommendations["id"].isin(taken_classes)]
    if for_metrics == False:
        recommendations = recommendations.head(top_n)

    return recommendations[["id", "name", "tags", "score"]]


# Example usage
user_id = 7
recommendations = hybrid_recommendation(
    user_id, content_weight=0.9, collab_weight=0.1, top_n=5
)
print(recommendations)
