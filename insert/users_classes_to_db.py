import json
import psycopg2
from psycopg2.extras import execute_values

data = json.loads(open("data/json/users_classes_generated.json").read())

conn = psycopg2.connect(
    dbname="hicoll", user="postgres", password="taufik09", host="localhost", port="5432"
)

cur = conn.cursor()

columns = ["user_id", "class_id", "rating"]
query = f"INSERT INTO users_classes ({','.join(columns)}) VALUES %s"

values = [[item[column] for column in columns] for item in data]

execute_values(cur, query, values)

conn.commit()

cur.close()
conn.close()

print("Data inserted successfully!")
