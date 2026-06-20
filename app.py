import streamlit as st
import pandas as pd
import sqlite3

from chatbot.sql_chain import ask_chatbot
from chatbot.response_formatter import format_response

from analytics.charts import (
    sales_chart,
    kpi_metrics,
    category_revenue_chart,
    monthly_trend_chart,
    gender_split_chart,
    age_distribution_chart,
    top_products_chart,
)
from analytics.insights import generate_insights

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Analytics AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0A0C14; color: #E2E8F0; }

/* Hide default Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #12151F;
    border-radius: 14px;
    padding: 6px 8px;
    border: 1px solid #1E2233;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 22px;
    font-size: 14px;
    font-weight: 500;
    color: #8892A4;
    background: transparent;
    border: none;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6C63FF, #5A54D4) !important;
    color: #fff !important;
    box-shadow: 0 4px 12px rgba(108,99,255,0.35);
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #1A1D2E, #12151F);
    border: 1px solid #252840;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(108,99,255,0.2);
}
.kpi-label { font-size: 12px; font-weight: 600; color: #6C63FF; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 8px; }
.kpi-value { font-size: 32px; font-weight: 700; color: #E2E8F0; }
.kpi-sub   { font-size: 12px; color: #8892A4; margin-top: 4px; }

/* Section headings */
.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #CBD5E0;
    border-left: 4px solid #6C63FF;
    padding-left: 12px;
    margin: 20px 0 12px;
}

/* Error box */
.error-box {
    background: linear-gradient(135deg, #2D0A0A, #1A0808);
    border: 1px solid #C53030;
    border-left: 5px solid #FC8181;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 16px 0;
}
.error-title { font-size: 15px; font-weight: 700; color: #FC8181; margin-bottom: 8px; }
.error-msg   { font-size: 13px; color: #FEB2B2; font-family: monospace; white-space: pre-wrap; word-break: break-all; }
.error-hint  { font-size: 12px; color: #8892A4; margin-top: 10px; }

/* SQL box */
.sql-box {
    background: #0D1117;
    border: 1px solid #252840;
    border-left: 4px solid #6C63FF;
    border-radius: 10px;
    padding: 14px 18px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #A9B7D0;
    overflow-x: auto;
    white-space: pre-wrap;
    margin: 10px 0;
}

/* Insight cards */
.insight-card {
    background: linear-gradient(145deg, #12151F, #1A1D2E);
    border: 1px solid #252840;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 14px;
    color: #CBD5E0;
    line-height: 1.6;
}

/* Header hero */
.hero {
    background: linear-gradient(135deg, #1A1D2E 0%, #12151F 100%);
    border: 1px solid #252840;
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(108,99,255,0.3), transparent 70%);
    border-radius: 50%;
}
.hero-title { font-size: 30px; font-weight: 700; color: #E2E8F0; margin: 0; }
.hero-sub   { font-size: 15px; color: #8892A4; margin: 8px 0 0; }
.hero-badge {
    display: inline-block;
    background: rgba(108,99,255,0.15);
    color: #9F97FF;
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 20px;
    font-size: 12px;
    padding: 4px 12px;
    margin-bottom: 12px;
    font-weight: 500;
}

/* Streamlit table override */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Chat input */
.stTextInput > div > div > input {
    background: #12151F;
    border: 1px solid #252840;
    border-radius: 10px;
    color: #E2E8F0;
    font-size: 14px;
    padding: 12px 16px;
}
.stTextInput > div > div > input:focus {
    border-color: #6C63FF;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.25);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #5A54D4);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(108,99,255,0.3);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(108,99,255,0.4);
}

/* Schema table */
.schema-row {
    display: flex;
    gap: 12px;
    padding: 10px 14px;
    border-bottom: 1px solid #1E2233;
    font-size: 13px;
}
.schema-col   { color: #9F97FF; font-family: monospace; font-weight: 600; flex: 2; }
.schema-type  { color: #F9A826; flex: 1; }
.schema-desc  { color: #8892A4; flex: 4; }
</style>
""", unsafe_allow_html=True)


# ─── Hero header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">✦ Powered by Gemini AI</div>
  <div class="hero-title">📊 Retail Analytics Intelligence</div>
  <div class="hero-sub">Ask questions in plain English · Explore dashboards · Understand your data</div>
</div>
""", unsafe_allow_html=True)


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊  Executive Dashboard", "🤖  AI Assistant", "🗃️  Database Explorer"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — EXECUTIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # KPI Metrics
    try:
        kpis = kpi_metrics()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">💰 Total Revenue</div>
              <div class="kpi-value">${kpis.get('total_revenue', 0):,.0f}</div>
              <div class="kpi-sub">Across all categories</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">🛒 Total Orders</div>
              <div class="kpi-value">{kpis.get('total_orders', 0):,.0f}</div>
              <div class="kpi-sub">Completed transactions</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">📦 Avg Order Value</div>
              <div class="kpi-value">${kpis.get('avg_order_value', 0):,.0f}</div>
              <div class="kpi-sub">Per transaction</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">👥 Unique Customers</div>
              <div class="kpi-value">{kpis.get('unique_customers', 0):,.0f}</div>
              <div class="kpi-sub">Distinct customer IDs</div>
            </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load KPIs: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    st.markdown('<div class="section-title">Revenue Overview</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])
    with col_a:
        try:
            st.plotly_chart(monthly_trend_chart(), use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")
    with col_b:
        try:
            st.plotly_chart(category_revenue_chart(), use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")

    # Charts row 2
    st.markdown('<div class="section-title">Customer Insights</div>', unsafe_allow_html=True)
    col_c, col_d, col_e = st.columns(3)
    with col_c:
        try:
            st.plotly_chart(gender_split_chart(), use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")
    with col_d:
        try:
            st.plotly_chart(age_distribution_chart(), use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")
    with col_e:
        try:
            st.plotly_chart(top_products_chart(), use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown('<div class="section-title">Ask a Retail Question</div>', unsafe_allow_html=True)

    # Example chips
    examples = [
        "Total revenue by product category",
        "Top 5 customers by spending",
        "Monthly sales trend for 2023",
        "Average order value by gender",
        "Electronics sales in 2023",
    ]
    st.markdown("**💡 Try these:**")
    chip_cols = st.columns(len(examples))
    selected_example = None
    for i, ex in enumerate(examples):
        if chip_cols[i].button(ex, key=f"ex_{i}"):
            selected_example = ex

    question = st.text_input(
        label="",
        placeholder="e.g. What are total sales by product category?",
        value=selected_example or "",
        key="question_input",
    )

    run_btn = st.button("⚡ Analyze", key="analyze_btn")

    if run_btn and question.strip():
        with st.spinner("🔍 Generating SQL & fetching results…"):
            try:
                sql_query, result = ask_chatbot(question)
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                  <div class="error-title">❌ Pipeline Error</div>
                  <div class="error-msg">{e}</div>
                  <div class="error-hint">Check your API key and network connection.</div>
                </div>""", unsafe_allow_html=True)
                st.stop()

        # ── Generated SQL ──────────────────────────────────────────────────
        st.markdown('<div class="section-title">Generated SQL</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sql-box">{sql_query}</div>', unsafe_allow_html=True)

        # ── SQL Error Handling ─────────────────────────────────────────────
        if isinstance(result, dict) and "error" in result:
            st.markdown(f"""
            <div class="error-box">
              <div class="error-title">❌ SQL Execution Failed</div>
              <div class="error-msg">{result['error']}</div>
              <div class="error-hint">💡 Tip: Try rephrasing your question with more specific column references, or check the Database Explorer tab for available columns.</div>
            </div>""", unsafe_allow_html=True)

        # ── Success path ───────────────────────────────────────────────────
        elif hasattr(result, "empty"):
            if result.empty:
                st.info("ℹ️ The query ran successfully but returned no rows.", icon="📭")
            else:
                # Results table
                st.markdown('<div class="section-title">Query Results</div>', unsafe_allow_html=True)
                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True,
                )

                # Chart
                chart = sales_chart(result)
                if chart:
                    st.markdown('<div class="section-title">Visualisation</div>', unsafe_allow_html=True)
                    st.plotly_chart(chart, use_container_width=True)

                # AI Insights
                st.markdown('<div class="section-title">🧠 AI Business Insights</div>', unsafe_allow_html=True)
                with st.spinner("Generating insights…"):
                    insights = generate_insights(result)
                for insight in insights:
                    st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

    elif run_btn and not question.strip():
        st.warning("Please enter a question before clicking Analyze.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — DATABASE EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown('<div class="section-title">Table: sales</div>', unsafe_allow_html=True)

    schema = [
        ("[Transaction ID]", "INTEGER", "Unique row identifier for each sale"),
        ("Date",             "TEXT",    "Transaction date in YYYY-MM-DD format"),
        ("[Customer ID]",    "TEXT",    "Unique customer identifier, e.g. CUST001"),
        ("Gender",           "TEXT",    "Customer gender: Male or Female"),
        ("Age",              "INTEGER", "Customer age in years"),
        ("[Product Category]","TEXT",   "Product category: Beauty, Clothing, or Electronics"),
        ("Quantity",         "INTEGER", "Number of units purchased"),
        ("[Price per Unit]", "INTEGER", "Price of a single unit"),
        ("[Total Amount]",   "INTEGER", "Total revenue for this transaction (Quantity × Price per Unit)"),
    ]

    st.markdown("""
    <div style="background:#12151F; border:1px solid #252840; border-radius:12px; overflow:hidden; margin-bottom:20px;">
      <div class="schema-row" style="background:#1A1D2E; font-weight:700; color:#CBD5E0;">
        <span style="flex:2;">Column</span>
        <span style="flex:1;">Type</span>
        <span style="flex:4;">Description</span>
      </div>
    """, unsafe_allow_html=True)

    for col, dtype, desc in schema:
        st.markdown(f"""
      <div class="schema-row">
        <span class="schema-col">{col}</span>
        <span class="schema-type">{dtype}</span>
        <span class="schema-desc">{desc}</span>
      </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Live sample data
    st.markdown('<div class="section-title">Sample Data (first 20 rows)</div>', unsafe_allow_html=True)
    try:
        conn = sqlite3.connect("database/retail.db")
        sample = pd.read_sql_query("SELECT * FROM sales LIMIT 20", conn)
        conn.close()
        st.dataframe(sample, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Could not load sample: {e}")

    # Suggested queries
    st.markdown('<div class="section-title">💬 Suggested Questions for the AI Assistant</div>', unsafe_allow_html=True)
    suggestions = [
        ("Total revenue per category",       "SELECT [Product Category], SUM([Total Amount]) AS Revenue FROM sales GROUP BY [Product Category]"),
        ("Top 5 highest spenders",           "SELECT [Customer ID], SUM([Total Amount]) AS Total_Spent FROM sales GROUP BY [Customer ID] ORDER BY Total_Spent DESC LIMIT 5"),
        ("Monthly revenue breakdown",        "SELECT strftime('%Y-%m', Date) AS Month, SUM([Total Amount]) AS Revenue FROM sales GROUP BY Month ORDER BY Month"),
        ("Gender revenue split",             "SELECT Gender, SUM([Total Amount]) AS Revenue FROM sales GROUP BY Gender"),
        ("Average age per category",         "SELECT [Product Category], ROUND(AVG(Age), 1) AS Avg_Age FROM sales GROUP BY [Product Category]"),
    ]
    for label, sql in suggestions:
        with st.expander(f"📌 {label}"):
            st.code(sql, language="sql")