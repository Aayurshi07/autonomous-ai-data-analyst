import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = os.path.join("db", "olist.db")


def get_daily_revenue():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT DATE(o.order_purchase_timestamp) AS order_date,
               SUM(oi.price) AS daily_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY order_date
        ORDER BY order_date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def detect_anomalies(df, threshold=2.0):
    mean_revenue = df["daily_revenue"].mean()
    std_revenue = df["daily_revenue"].std()

    df["z_score"] = (df["daily_revenue"] - mean_revenue) / std_revenue
    df["is_anomaly"] = df["z_score"].abs() > threshold

    anomalies = df[df["is_anomaly"]].copy()
    return df, anomalies



if __name__ == "__main__":
    df = get_daily_revenue()
    print(f"Loaded {len(df)} days of revenue data\n")

    df, anomalies = detect_anomalies(df)

    print(f"Found {len(anomalies)} anomalous days (|z-score| > 2.0):\n")
    for _, row in anomalies.iterrows():
        direction = "SPIKE" if row["z_score"] > 0 else "DROP"
        print(f"  {row['order_date']}: ${row['daily_revenue']:,.2f}  "
              f"(z-score: {row['z_score']:.2f}, {direction})")