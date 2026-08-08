\# Autonomous AI Data Analyst



A GenAI-powered analytics tool that answers natural-language questions about e-commerce data via LLM-generated SQL, and proactively surfaces insights by detecting statistical anomalies and generating narrative summaries.



\*\*Live app:\*\* \[autonomous-ai-data-analyst-2msbxvxyw2x2cwufnlz45w.streamlit.app](https://autonomous-ai-data-analyst-2msbxvxyw2x2cwufnlz45w.streamlit.app)



> Hosted on Streamlit Community Cloud's free tier, which sleeps after 12 hours of inactivity. A scheduled GitHub Actions workflow pings the app every 6 hours to minimize downtime; if the app is asleep, a single click restores it in under a minute.



\## Overview



The application has two core capabilities:



1\. \*\*Text-to-SQL agent\*\* — accepts a natural-language question, generates a SQL query against a relational schema using Gemini, validates the query for safety, executes it, and returns results. If execution fails, the failing query and error message are fed back to the model for correction, up to three attempts.

2\. \*\*Proactive anomaly detection and narrative generation\*\* — computes daily revenue, flags statistically significant deviations using Z-scores, and generates a plain-language summary explaining the detected anomalies, without requiring a user query.



This combination — reactive question-answering plus proactive insight surfacing — mirrors the direction of current BI tooling (Power BI Copilot, Tableau Pulse, ThoughtSpot Spotter) rather than a single-shot chatbot wrapper.



\## Architecture



```

Source CSVs

&#x20;   │

&#x20;   ▼

SQLite database (indexed, relational, built on first run)

&#x20;   │

&#x20;   ├──► Text-to-SQL agent ──► safety validation ──► execution ──► retry on failure

&#x20;   │

&#x20;   └──► Z-score anomaly detection ──► narrative generation (Gemini)

&#x20;                                             │

&#x20;                                             ▼

&#x20;                                   Streamlit interface

&#x20;                                   (Chat tab / Insights tab)

```



\## Tech stack



| Component | Choice |

|---|---|

| Dataset | \[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — \~100K orders, 9 relational tables |

| Database | SQLite, indexed on join columns |

| LLM | Google Gemini (`gemini-flash-latest`) via `google-genai` |

| Anomaly detection | Z-score (pandas / numpy) |

| Interface | Streamlit |

| Deployment | Streamlit Community Cloud + GitHub Actions (uptime ping) |



\## Example queries



\- "What are the top 5 product categories by revenue?"

\- "Which state has the slowest average delivery time?"

\- "What is the correlation between review score and shipping cost?" — SQLite has no built-in `CORR()` function; the agent handles this by generating the Pearson correlation formula directly from `AVG`/`SQRT`.



The anomaly detector correctly identified \*\*November 24, 2017 (Black Friday)\*\* as the largest revenue anomaly in the dataset (Z-score of 10.4), without being given any calendar or holiday information.



\## Limitations



\- \*\*Semantic correctness is not guaranteed.\*\* When asked for "profit margin per seller" — a metric the schema does not support, since no cost data exists — the agent generated a syntactically valid query (`(price − freight\_value) / price`) that treats shipping cost as cost of goods. The query executed without error but the result is not a meaningful profit margin. This reflects a general limitation of text-to-SQL systems: syntactic validity does not imply semantic validity. A plausibility or confidence check prior to displaying results would be a natural extension.

\- \*\*Anomaly detection in this dataset only flagged revenue spikes, not drops.\*\* The detection logic checks both directions (`abs(z-score) > threshold`); the absence of flagged drops reflects the underlying data over the analyzed period, not an asymmetry in the detection method.

\- \*\*Free-tier hosting sleeps after inactivity\*\*, mitigated but not eliminated by the scheduled keep-alive workflow.

\- \*\*The database is not committed to the repository.\*\* It is rebuilt from source CSVs on first run to avoid storing a large binary file in version control; this adds a short delay on a cold start.



\## Local setup



```bash

git clone https://github.com/Aayurshi07/autonomous-ai-data-analyst.git

cd autonomous-ai-data-analyst

pip install -r requirements.txt

```



Create a `.env` file in the project root:

```

GEMINI\_API\_KEY=your\_key\_here

```



Run:

```bash

streamlit run app.py

```



The database is built automatically from `data/\*.csv` on first run if `db/olist.db` does not already exist.



\## Repository structure



```

├── app.py                      # Streamlit interface

├── scripts/

│   ├── load\_data.py            # CSV → indexed SQLite

│   ├── text\_to\_sql.py          # Text-to-SQL agent with retry logic

│   ├── anomaly\_detection.py    # Z-score anomaly detection

│   └── narrative.py            # Narrative generation

├── queries/

│   └── ground\_truth.sql        # Hand-written queries used to validate agent output

├── data/                       # Source CSVs

├── .github/workflows/          # Keep-alive workflow

└── requirements.txt

```

