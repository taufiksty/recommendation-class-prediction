import json
import random
from faker import Faker

fake = Faker("id_ID")
interests = [
    "programming",
    "backend development",
    "web development",
    "business intelligence",
    "product management",
    "agile",
    "programming",
    "python",
    "data visualization",
    "business intelligence",
    "enterprise system",
    "product management",
    "programming",
    "backend development",
    "web development",
    "agile",
    "product management",
    "business intelligence",
    "programming",
    "data science",
    "machine learning",
    "business intelligence",
    "management",
    "data analysis",
    "cyber security",
    "network",
    "hacking",
    "cloud computing",
    "devops",
    "network",
    "programming",
    "mobile development",
    "cross platform",
    "network",
    "cloud computing",
    "management",
    "programming",
    "frontend development",
    "web development",
    "programming",
    "database",
    "sql",
    "programming",
    "mobile development",
    "cross platform",
    "programming",
    "data visualization",
    "data science",
    "programming",
    "monitoring",
    "system analytics",
    "programming",
    "frontend development",
    "web development",
    "UI/UX",
    "research",
    "web design",
    "programming",
    "frontend development",
    "web development",
    "big data",
    "database",
    "data analysis",
    "programming",
    "testing",
    "benchmarking",
    "data science",
    "machine learning",
    "AI",
    "machine learning",
    "data science",
    "AI",
    "database",
    "enterprise system",
    "big data",
    "database",
    "data analysis",
    "sql",
    "database",
    "data analysis",
    "sql",
    "programming",
    "data science",
    "backend development",
    "it governance",
    "business intelligence",
    "product management",
    "it governance",
    "business intelligence",
    "product management",
    "linux",
    "devops",
    "cloud computing",
    "programming",
    "frontend development",
    "web development",
    "programming",
    "mobile development",
    "android development",
    "language",
    "korean",
    "communication",
    "language",
    "mandarin",
    "communication",
    "language",
    "english",
    "communication",
    "language",
    "japanese",
    "communication",
    "softskill",
    "spreadsheet",
    "data analysis",
    "softskill",
    "spreadsheet",
    "data analysis",
    "UI/UX",
    "web design",
    "research",
    "digital marketing",
    "social media",
    "SEO",
    "business intelligence",
    "digital marketing",
    "product management",
    "business intelligence",
    "softskill",
    "communication",
    "communication",
    "softskill",
    "business intelligence",
]
genders = ["male", "female"]

data = json.loads(open("data/json/users.json").read())


def generate_user_data(num_users):
    users = data

    for i in range(4, num_users + 4):
        created_at = fake.iso8601(tzinfo=None)

        user_interests = []
        while len(user_interests) < 3:
            while True:
                interest = random.choice(interests)
                if interest not in user_interests:
                    user_interests.append(interest)
                    break

        user = {
            "id": i,
            "fullname": fake.name(),
            "email": fake.email(),
            "phone_number": f"628{random.randint(100000000, 999999999)}",
            "gender": random.choice(genders),
            "birthdate": fake.date_of_birth(minimum_age=16, maximum_age=55).isoformat(),
            "image": "https://t9003038375.p.clickup-attachments.com/t9003038375/5cfa9b89-6967-420b-a341-e06a62b734f7/Handikawj.png?view=open",
            "interests": user_interests,
            "is_active": True,
            "is_first_login": False,
            "password": "password",
            "token": None,
            "user_type_id": 3,
            "description": None,
            "linkedin_url": None,
            "created_at": created_at,
            "updated_at": created_at,
        }

        users.append(user)

    return users


synthetic_users = generate_user_data(45)

with open("data/json/users_generated.json", "w") as output_file:
    json.dump(synthetic_users, output_file, indent=2, ensure_ascii=False)

print(
    "Synthetic user data has been generated and saved to 'data/json/users_generated.json'."
)
