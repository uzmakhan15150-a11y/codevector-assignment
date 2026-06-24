import psycopg2
import os
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

load_dotenv()

CATEGORIES = ["Electronics", "Clothing", "Books", "Food", "Sports", "Home", "Beauty", "Toys"]

def seed():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    conn.commit()

    # Bulk insert 200,000 products
    print("Inserting 200,000 products...")
    batch_size = 5000
    total = 200000
    base_time = datetime.now() - timedelta(days=365)

    for batch_start in range(0, total, batch_size):
        records = []
        for i in range(batch_size):
            name = f"Product {batch_start + i + 1}"
            category = random.choice(CATEGORIES)
            price = round(random.uniform(10, 10000), 2)
            created_at = base_time + timedelta(seconds=batch_start + i)
            records.append((name, category, price, created_at, created_at))

        cur.executemany(
            "INSERT INTO products (name, category, price, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            records
        )
        conn.commit()
        print(f"Inserted {min(batch_start + batch_size, total)} / {total}")

    cur.close()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    seed()