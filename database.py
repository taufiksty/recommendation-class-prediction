from sqlalchemy import create_engine
import pandas as pd
import re


def get_db_connection():
    DATABASE_URI = "postgresql+psycopg2://postgres:taufik09@localhost:5432/hicoll"
    engine = create_engine(DATABASE_URI)
    return engine


def load_data_from_db():
    engine = get_db_connection()

    users = pd.read_sql("SELECT id, interests FROM users", con=engine)
    classes = pd.read_sql("SELECT * FROM classes", con=engine)
    users_classes = pd.read_sql(
        "SELECT user_id, class_id, rating FROM users_classes", con=engine
    )

    def parse_interests_or_tags(interest_or_tags_str):
        try:
            return interest_or_tags_str.strip("{}").replace('"', "").lower().split(",")
        except Exception as e:
            print(f"Failed to parse interests: {interest_or_tags_str}, error: {e}")
            return []

    users["interests"] = users["interests"].apply(parse_interests_or_tags)
    classes["tags"] = classes["tags"].apply(parse_interests_or_tags)

    return users, classes, users_classes
