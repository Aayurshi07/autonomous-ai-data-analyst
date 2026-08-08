import streamlit as st
import sys
import os
import plotly.express as px

sys.path.append("scripts")
from text_to_sql import generate_sql, is_safe_sql, run_query
from anomaly_detection import get_daily_revenue, detect_anomalies
from narrative import generate_narrative

st.set_page_config(page_title="Autonomous AI Data Analyst", layout="wide")

st.title("🤖 Autonomous AI Data Analyst")
st.caption("Ask questions about Olist e-commerce data, or explore proactively detected insights")

tab1, tab2 = st.tabs(["💬 Chat", "📊 Insights"])

with tab1:
    st.subheader("Ask a question about the data")
    question = st.text_input("Your question:", placeholder="e.g. What are the top 5 product categories by revenue?")

    if st.button("Ask"):
        if question:
            with st.spinner("Thinking..."):
                sql = generate_sql(question)
                max_attempts = 3
                attempt = 1
                success = False

                while attempt <= max_attempts:
                    if not is_safe_sql(sql):
                        st.error("This query was blocked for safety reasons.")
                        break

                    columns, result = run_query(sql)

                    if columns is not None:
                        success = True
                        break
                    else:
                        if attempt < max_attempts:
                            sql = generate_sql(question, previous_sql=sql, error_message=result)
                        attempt += 1

            if success:
                st.code(sql, language="sql")
                st.dataframe([dict(zip(columns, row)) for row in result])
            else:
                st.error(f"Could not generate a working query after {max_attempts} attempts.")
        else:
            st.warning("Please enter a question.")

with tab2:
    st.subheader("Proactively Detected Insights")

    if st.button("Run Anomaly Detection"):
        with st.spinner("Analyzing revenue patterns..."):
            df = get_daily_revenue()
            df, anomalies = detect_anomalies(df)

        st.write(f"Found **{len(anomalies)}** anomalous days out of {len(df)} total days analyzed.")

        fig = px.line(df, x="order_date", y="daily_revenue", title="Daily Revenue Over Time")
        anomaly_points = df[df["is_anomaly"]]
        fig.add_scatter(x=anomaly_points["order_date"], y=anomaly_points["daily_revenue"],
                         mode="markers", marker=dict(color="red", size=10), name="Anomaly")
        st.plotly_chart(fig, use_container_width=True)

        if len(anomalies) > 0:
            with st.spinner("Generating narrative summary..."):
                summary = generate_narrative(anomalies)
            st.subheader("AI-Generated Summary")
            st.write(summary)

            st.subheader("Anomaly Details")
            st.dataframe(anomalies[["order_date", "daily_revenue", "z_score"]])