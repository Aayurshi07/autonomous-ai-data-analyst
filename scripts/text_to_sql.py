import os
import sqlite3
from dotenv import load_dotenv
from google import genai

load_dotenv()

DB_PATH = os.path.join("db", "olist.db")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

SCHEMA = """
Tables:

customers(customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)

orders(order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, 
       order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date)

order_items(order_id, order_item_id, product_id, seller_id, price, freight_value)

payments(order_id, payment_sequential, payment_type, payment_installments, payment_value)

reviews(review_id, order_id, review_score, review_comment_title, review_comment_message)

products(product_id, product_category_name, product_weight_g, product_length_cm, 
          product_height_cm, product_width_cm)

sellers(seller_id, seller_zip_code_prefix, seller_city, seller_state)

category_translation(product_category_name, product_category_name_english)
"""


def generate_sql(question):
    prompt = f"""You are a SQL expert. Given this database schema:

{SCHEMA}

Write a SQLite query to answer this question: "{question}"

Rules:
- Only use SELECT statements, never modify data
- Return ONLY the SQL query, no explanation, no markdown formatting, no backticks
- Use proper JOINs based on the schema above
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    sql = response.text.strip()
    return sql

def is_safe_sql(sql):
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]
    sql_upper = sql.upper()
    for word in forbidden:
        if word in sql_upper:
            return False
    return True  

def run_query(sql):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        columns = [description[0] for description in cur.description]
        rows = cur.fetchall()
        conn.close()
        return columns, rows
    except Exception as e:
        conn.close()
        return None, str(e)

if __name__ == "__main__":
    print("Autonomous AI Data Analyst — Text-to-SQL")
    print("Ask a question about the Olist e-commerce data (or type 'exit' to quit)\n")

    while True:
        question = input("Your question: ")
        if question.lower() == "exit":
            break

        sql = generate_sql(question)
        print(f"\nGenerated SQL:\n{sql}\n")

        if not is_safe_sql(sql):
            print("This query was blocked for safety reasons.\n")
            continue

        columns, result = run_query(sql)

        if columns is None:
            print(f"Query failed: {result}\n")
        else:
            print(columns)
            for row in result[:10]:
                print(row)
            print()