import json
import psycopg2
from psycopg2.extras import execute_values

data = json.loads(open("data/json/users_generated.json").read())

conn = psycopg2.connect(
    dbname="hicoll", user="postgres", password="taufik09", host="localhost", port="5432"
)

cur = conn.cursor()

columns = [
    "fullname",
    "email",
    "phone_number",
    "gender",
    "birthdate",
    "image",
    "interests",
    "is_active",
    "is_first_login",
    "password",
    "token",
    "user_type_id",
    "description",
    "linkedin_url",
]
query = f"INSERT INTO users ({','.join(columns)}) VALUES %s"

values = [[item[column] for column in columns] for item in data]

execute_values(cur, query, values)

conn.commit()

cur.close()
conn.close()

print("Data inserted successfully!")
