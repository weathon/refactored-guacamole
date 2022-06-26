import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"])
def run(sql):
    with conn.cursor() as cur:
        cur.execute(input())
        res = cur.fetchall()
        conn.commit()
        print(res)
