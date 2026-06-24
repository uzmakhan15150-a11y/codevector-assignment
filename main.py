from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/products")
def get_products(
    limit: int = 20,
    cursor_created_at: Optional[str] = None,
    cursor_id: Optional[int] = None,
    category: Optional[str] = None
):
    conn = get_conn()
    cur = conn.cursor()

    params = []
    where_clauses = []

    if category:
        where_clauses.append("category = %s")
        params.append(category)

    if cursor_created_at and cursor_id:
        where_clauses.append("(created_at, id) < (%s, %s)")
        params.extend([cursor_created_at, cursor_id])

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    params.append(limit)

    query = f"""
        SELECT id, name, category, price, created_at, updated_at
        FROM products
        {where_sql}
        ORDER BY created_at DESC, id DESC
        LIMIT %s
    """

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price": float(row[3]),
            "created_at": str(row[4]),
            "updated_at": str(row[5])
        })

    next_cursor = None
    if len(products) == limit:
        last = products[-1]
        next_cursor = {
            "created_at": last["created_at"],
            "id": last["id"]
        }

    return {
        "products": products,
        "next_cursor": next_cursor
    }

@app.get("/")
def root():
    return {"message": "CodeVector Products API is running!"}
git add .
git commit -m "Add get product by id endpoint"
git push