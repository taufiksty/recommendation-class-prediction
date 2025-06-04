from main_v3 import hybrid_recommendation
import pandas as pd
from database import load_data_from_db

users, classes, users_classes = load_data_from_db()


def calculate_diversity(recommendations):
    tags = recommendations["tags"].tolist()
    flattened_tags = [tag for sublist in tags for tag in sublist]
    unique_tags = len(set(flattened_tags))
    total_tags = len(flattened_tags)
    diversity_score = unique_tags / total_tags if total_tags > 0 else 0
    return diversity_score


def calculate_novelty(user_id, recommendations):
    # Classes the user has already taken
    taken_classes = users_classes[users_classes["user_id"] == user_id][
        "class_id"
    ].tolist()

    # Recommended classes that are new
    new_recommendations = [
        cls_id for cls_id in recommendations["id"] if cls_id not in taken_classes
    ]
    novelty_score = (
        len(new_recommendations) / len(recommendations)
        if len(recommendations) > 0
        else 0
    )
    return novelty_score


def calculate_mean_predicted_rating(recommendations):
    mean_rating = recommendations["score"].mean()
    return mean_rating


def calculate_coverage(recommendations, total_classes):
    recommended_classes = recommendations["id"].tolist()
    coverage_score = (
        len(recommended_classes) / total_classes if total_classes > 0 else 0
    )
    return coverage_score


def evaluate_recommendations(user_id, top_n=3):
    # Get recommendations for the user
    recommendations = hybrid_recommendation(
        user_id, content_weight=0.7, collab_weight=0.3, for_metrics=True
    )
    recommendations_top3 = recommendations.head(top_n)

    # Metrics calculation
    diversity = calculate_diversity(recommendations_top3)
    novelty = calculate_novelty(user_id, recommendations_top3)
    mean_predicted_rating = calculate_mean_predicted_rating(recommendations_top3)
    coverage = calculate_coverage(recommendations, total_classes=classes.shape[0])

    # Print results
    # print(f"User ID: {user_id}")
    # print(f"User Interests: {users[users['id'] == user_id]['interests'].iloc[0]}")
    # print(
    #     f"Recommended Classes: {recommendations[['id', 'name', 'tags', 'score']].to_dict('records')}"
    # )
    # print(f"Diversity: {diversity:.4f}")
    # print(f"Novelty: {novelty:.4f}")
    # print(f"Mean Predicted Rating: {mean_predicted_rating:.4f}")
    # print(f"Coverage: {coverage:.4f}")
    # print("=" * 50)

    return diversity, novelty, mean_predicted_rating, coverage


# Example Usage for Multiple Users
user_ids = users["id"].tolist()[24:34]  # Evaluate for first 10 users
results = []


for user_id in user_ids:
    metrics = evaluate_recommendations(user_id)
    results.append(
        {
            "user_id": user_id,
            "diversity": metrics[0],
            "novelty": metrics[1],
            "mean_rating": metrics[2],
            "coverage": metrics[3],
        }
    )

# Convert results to DataFrame for analysis
results_df = pd.DataFrame(results)
print(results_df)
print("\n")
print("Average Diversity:", results_df["diversity"].mean())
print("Average Novelty:", results_df["novelty"].mean())
print("Average Mean Rating:", results_df["mean_rating"].mean())
print("Average Coverage:", results_df["coverage"].mean())
