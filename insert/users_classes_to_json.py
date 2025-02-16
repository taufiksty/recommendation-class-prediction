import random
import json
import numpy as np
from faker import Faker

fake = Faker("id_ID")


def generate_users_classes(num_data):
    users_classes = []

    user_id_range = (4, 48)
    class_id_range = (1, 44)

    # Calculate total unique combinations
    total_combinations = (user_id_range[1] - user_id_range[0] + 1) * (
        class_id_range[1] - class_id_range[0] + 1
    )
    if num_data > total_combinations:
        raise ValueError(
            f"num_data exceeds the total possible unique combinations ({total_combinations})."
        )

    # Generate unique combinations efficiently
    all_combinations = np.array(
        [
            (user_id, class_id)
            for user_id in range(user_id_range[0], user_id_range[1] + 1)
            for class_id in range(class_id_range[0], class_id_range[1] + 1)
        ]
    )
    selected_combinations = all_combinations[
        np.random.choice(all_combinations.shape[0], num_data, replace=False)
    ]

    # Generate user-class data
    for i, (user_id, class_id) in enumerate(selected_combinations, start=1):
        users_classes.append(
            {
                "id": i,
                "user_id": int(user_id),
                "class_id": int(class_id),
                "rating": random.randint(4, 5),
            }
        )

    return users_classes


# Generate synthetic data
synthetic_users_classes = generate_users_classes(500)

# Save to JSON
with open("data/json/users_classes_generated.json", "w") as output_file:
    json.dump(synthetic_users_classes, output_file, indent=2, ensure_ascii=False)

print(
    "Users Classes data generated and saved to data/json/users_classes_generated.json"
)
