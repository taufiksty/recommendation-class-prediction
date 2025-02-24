import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
from database import load_data_from_db

users, classes, users_classes = load_data_from_db()


# 1. Content-Based Filtering (CBF)
def content_based_filtering(user_id):
    user = users[users["id"] == user_id].iloc[0]
    user_interests = ",".join(user["interests"])

    classes_tags = classes["tags"].apply(
        lambda x: ",".join(x) if isinstance(x, list) else x
    )

    # TF-IDF Vectorization
    tfidf = TfidfVectorizer(stop_words="english")
    class_features = tfidf.fit_transform(classes_tags)
    user_vector = tfidf.transform([user_interests])

    # Calculate cosine similarity
    similarity = cosine_similarity(user_vector, class_features).flatten()
    print(f"Raw Similarity Scores: {similarity}")

    if similarity.max() == similarity.min():
        print("Warning: All similarity scores are the same, normalization will fail!")
        return np.zeros(len(classes))

    # Normalize scores
    similarity_normalized = (similarity - similarity.min()) / (
        similarity.max() - similarity.min()
    )

    print(f"Normalized Similarity Scores: {similarity_normalized}")
    return similarity_normalized


# 2. Collaborative Filtering (CF)
def collaborative_filtering(user_id):
    interactions = users_classes.pivot(
        index="user_id", columns="class_id", values="rating"
    ).fillna(0)

    if user_id not in interactions.index:
        print(f"User {user_id} not found in interactions! Returning zeros.")
        return np.zeros(len(classes))  # User never interacted

    user_ratings = interactions.values
    user_means = np.mean(user_ratings, axis=1)

    if np.all(user_ratings == 0):
        print(f"User {user_id} has no ratings! Returning zeros.")
        return np.zeros(len(classes))

    user_ratings_demeaned = user_ratings - user_means.reshape(-1, 1)

    try:
        U, sigma, Vt = svds(user_ratings_demeaned, k=min(20, len(user_ratings) - 1))
        sigma = np.diag(sigma)

        predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_means.reshape(-1, 1)
        predictions_df = pd.DataFrame(predicted_ratings, columns=interactions.columns, index=interactions.index)

        predictions = predictions_df.loc[user_id].values

        if predictions.max() == predictions.min():
            print("Warning: All predictions are the same, skipping normalization!")
            return np.zeros(len(classes))

        predictions_normalized = (predictions - predictions.min()) / (
            predictions.max() - predictions.min()
        )

        return predictions_normalized

    except Exception as e:
        print(f"Error in collaborative filtering: {e}")
        return np.zeros(len(classes))  # If SVD fails



# 3. Hybrid Recommendation
def hybrid_recommendation(user_id, content_weight=0.7, collab_weight=0.3, top_n=3):
    content_scores = content_based_filtering(user_id)
    collaborative_scores = collaborative_filtering(user_id)

    if np.all(collaborative_scores == 0):
        print("Collaborative filtering failed. Using only content-based filtering.")
        hybrid_scores = content_scores  # Ignore collaborative filtering
    else:
        hybrid_scores = (content_weight * content_scores) + (collab_weight * collaborative_scores)

    print(f"Final Hybrid Scores: {hybrid_scores}")

    recommendations = classes.copy()
    recommendations["score"] = hybrid_scores
    recommendations = recommendations.sort_values("score", ascending=False)

    taken_classes = users_classes[users_classes["user_id"] == user_id]["class_id"].tolist()
    recommendations = recommendations[~recommendations["id"].isin(taken_classes)]

    return recommendations.head(top_n)

