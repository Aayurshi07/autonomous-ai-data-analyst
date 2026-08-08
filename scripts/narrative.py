import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def generate_narrative(anomalies_df):
    if len(anomalies_df) == 0:
        return "No significant anomalies detected in the data."

    anomaly_lines = []
    for _, row in anomalies_df.iterrows():
        direction = "spike" if row["z_score"] > 0 else "drop"
        anomaly_lines.append(
            f"- {row['order_date']}: ${row['daily_revenue']:,.2f} "
            f"({direction}, z-score: {row['z_score']:.2f})"
        )
    anomaly_text = "\n".join(anomaly_lines)

    prompt = f"""You are a data analyst writing a brief weekly summary for a business stakeholder.

Here are statistically significant anomalies detected in daily e-commerce revenue:

{anomaly_text}

Write a short, natural-language summary (3-5 sentences) explaining what happened and a plausible reason why, 
the way a junior analyst would write a "here's what happened" report. If a date looks like it could align with 
a known shopping event (like Black Friday, Christmas, etc.), mention that as a likely explanation. 
Be concise and business-friendly, not technical.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()

if __name__ == "__main__":
    import sys
    sys.path.append("scripts")
    from anomaly_detection import get_daily_revenue, detect_anomalies

    print("Fetching revenue data and detecting anomalies...\n")
    df = get_daily_revenue()
    df, anomalies = detect_anomalies(df)

    print(f"Found {len(anomalies)} anomalies. Generating narrative summary...\n")
    summary = generate_narrative(anomalies)

    print("=" * 60)
    print("WEEKLY INSIGHT SUMMARY")
    print("=" * 60)
    print(summary)
    print("=" * 60)