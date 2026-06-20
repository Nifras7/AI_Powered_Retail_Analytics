import pandas as pd
from chatbot.llm import load_llm

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = load_llm()
    return _llm


def generate_insights(df: pd.DataFrame) -> list[str]:
    """
    Use Gemini to produce 3 concise business insights from the query result.
    Returns a list of insight strings.
    """
    if df is None or df.empty:
        return ["No data returned — try rephrasing your question."]

    # Build a compact text summary to keep token usage low
    summary = df.to_string(index=False, max_rows=20)
    row_count = len(df)
    col_names = ", ".join(df.columns.tolist())

    prompt = f"""You are an expert retail business analyst.
Below is a query result with {row_count} rows and columns: {col_names}.

Data:
{summary}

Generate exactly 3 short, actionable business insights from this data.
Format each insight as a single sentence starting with an emoji.
Do NOT use bullet points, markdown, or numbered lists — just 3 lines separated by newlines.
"""
    try:
        response = _get_llm().invoke(prompt)
        lines = [l.strip() for l in response.content.strip().splitlines() if l.strip()]
        return lines[:3] if lines else ["✅ Data retrieved successfully."]
    except Exception as e:
        return [f"⚠️ Could not generate insights: {e}"]