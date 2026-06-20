import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3

DB_PATH = "database/retail.db"

# ─── Colour palette ───────────────────────────────────────────────────────────
PALETTE = ["#6C63FF", "#FF6584", "#43BCCD", "#F9A826", "#44CF6C", "#E05C5C"]
DARK_BG = "#0F1117"
CARD_BG = "#1A1D27"
TEXT     = "#E2E8F0"
GRID     = "#2D3748"


def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT, size=16)),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="Inter, sans-serif"),
        xaxis=dict(gridcolor=GRID, showline=False, tickfont=dict(color=TEXT)),
        yaxis=dict(gridcolor=GRID, showline=False, tickfont=dict(color=TEXT)),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
        hoverlabel=dict(bgcolor=CARD_BG, font_size=13, font_color=TEXT),
    )
    return fig


# ─── Query result chart (used by AI Assistant tab) ───────────────────────────
def sales_chart(df: pd.DataFrame) -> go.Figure:
    """Intelligently pick the best chart based on the DataFrame shape."""
    if df is None or df.empty:
        return None

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols    = df.select_dtypes(exclude="number").columns.tolist()

    # Single scalar result
    if len(df) == 1 and len(numeric_cols) == 1:
        val  = df[numeric_cols[0]].iloc[0]
        label = numeric_cols[0]
        fig  = go.Figure(go.Indicator(
            mode="number",
            value=float(val),
            title={"text": label, "font": {"color": TEXT, "size": 18}},
            number={"font": {"color": "#6C63FF", "size": 52}},
        ))
        fig.update_layout(paper_bgcolor=DARK_BG, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    # Category vs numeric
    if text_cols and numeric_cols:
        x_col, y_col = text_cols[0], numeric_cols[0]
        fig = px.bar(df, x=x_col, y=y_col,
                     color_discrete_sequence=PALETTE,
                     labels={y_col: y_col, x_col: x_col})
        return _base_layout(fig, f"{y_col} by {x_col}")

    # Two numeric columns → scatter
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                         color_discrete_sequence=PALETTE)
        return _base_layout(fig, f"{numeric_cols[0]} vs {numeric_cols[1]}")

    # Fallback: plain table-like bar of first numeric
    if numeric_cols:
        fig = px.bar(df, y=numeric_cols[0], color_discrete_sequence=PALETTE)
        return _base_layout(fig)

    return None


# ─── Dashboard charts (pre-built from full DB) ───────────────────────────────
def _load(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def kpi_metrics() -> dict:
    """Return headline KPI numbers."""
    df = _load("""
        SELECT
            SUM([Total Amount])  AS total_revenue,
            COUNT(*)             AS total_orders,
            ROUND(AVG([Total Amount]), 2) AS avg_order_value,
            COUNT(DISTINCT [Customer ID]) AS unique_customers
        FROM sales
    """)
    return df.iloc[0].to_dict()


def category_revenue_chart() -> go.Figure:
    df = _load("""
        SELECT [Product Category] AS Category,
               SUM([Total Amount]) AS Revenue
        FROM sales
        GROUP BY [Product Category]
        ORDER BY Revenue DESC
    """)
    fig = px.pie(df, names="Category", values="Revenue",
                 color_discrete_sequence=PALETTE, hole=0.5)
    fig.update_traces(textfont_color=TEXT, textposition="outside")
    return _base_layout(fig, "Revenue by Category")


def monthly_trend_chart() -> go.Figure:
    df = _load("""
        SELECT strftime('%Y-%m', Date) AS Month,
               SUM([Total Amount]) AS Revenue
        FROM sales
        GROUP BY Month
        ORDER BY Month
    """)
    fig = px.area(df, x="Month", y="Revenue",
                  color_discrete_sequence=["#6C63FF"],
                  markers=True)
    fig.update_traces(line_color="#6C63FF", fillcolor="rgba(108,99,255,0.15)")
    return _base_layout(fig, "Monthly Revenue Trend")


def gender_split_chart() -> go.Figure:
    df = _load("""
        SELECT Gender,
               SUM([Total Amount]) AS Revenue
        FROM sales
        GROUP BY Gender
    """)
    fig = px.bar(df, x="Gender", y="Revenue",
                 color="Gender",
                 color_discrete_sequence=["#6C63FF", "#FF6584"])
    return _base_layout(fig, "Revenue by Gender")


def age_distribution_chart() -> go.Figure:
    df = _load("SELECT Age FROM sales")
    fig = px.histogram(df, x="Age", nbins=20,
                       color_discrete_sequence=["#43BCCD"])
    fig.update_traces(marker_line_width=0)
    return _base_layout(fig, "Customer Age Distribution")


def top_products_chart() -> go.Figure:
    df = _load("""
        SELECT [Product Category] AS Category,
               SUM(Quantity) AS Units_Sold
        FROM sales
        GROUP BY Category
        ORDER BY Units_Sold DESC
    """)
    fig = px.bar(df, x="Units_Sold", y="Category",
                 orientation="h",
                 color_discrete_sequence=["#F9A826"])
    return _base_layout(fig, "Units Sold by Category")