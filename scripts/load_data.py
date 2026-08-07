import sqlite3
import pandas as pd
import os

DATA_DIR = "data"
DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "olist.db")

os.makedirs(DB_DIR, exist_ok=True)

FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}

def load_csv_to_sqlite(conn):
    for filename, table_name in FILES.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"  [SKIP] {filename} not found in {DATA_DIR}/ — check your download")
            continue

        df = pd.read_csv(path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"  [OK] {table_name}: {len(df):,} rows loaded")
def add_indexes(conn):
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_items_product ON order_items(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_items_seller ON order_items(seller_id);",
        "CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_order ON reviews(order_id);",
    ]
    cur = conn.cursor()
    for stmt in index_statements:
        cur.execute(stmt)
    conn.commit()
    print("  Indexes created.")    

def sanity_check(conn):
    cur = conn.cursor()
    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    print("\nTables in DB:", [t[0] for t in tables])

    test_query = """
        SELECT COUNT(*) 
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id;
    """
    result = cur.execute(test_query).fetchone()
    print(f"Join test (orders + items + customers): {result[0]:,} matched rows")




if __name__ == "__main__":
    print(f"Loading Olist CSVs from ./{DATA_DIR}/ into {DB_PATH} ...\n")
    conn = sqlite3.connect(DB_PATH)

    load_csv_to_sqlite(conn)
    add_indexes(conn)
    sanity_check(conn)

    conn.close()
    print(f"\nDone. Database saved at {DB_PATH}")



