import json
import psycopg2
from psycopg2.extras import execute_values

data = json.loads(open("data/json/classes.json").read())

conn = psycopg2.connect(
    dbname="hicoll", user="postgres", password="taufik09", host="localhost", port="5432"
)

cur = conn.cursor()

columns = [
    "name",
    "image",
    "thumbnail",
    "description",
    "meta_description",
    "level",
    "class_category_id",
    "tags",
    "slug",
    "method",
    "media",
    "prefix_code",
    "materials",
    "collaboration_feed",
    "instructor_id",
    "learning_link",
    "consultancy_link",
    "consultancy_schedule",
    "group_chat_link",
    "price",
    "registration_close_date",
]
query = f"INSERT INTO classes ({','.join(columns)}) VALUES %s"

values = [[item[column] for column in columns] for item in data]

execute_values(cur, query, values)

conn.commit()

cur.close()
conn.close()

print("Data inserted successfully!")
