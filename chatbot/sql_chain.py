import re
from chatbot.llm import load_llm
from chatbot.prompts import SYSTEM_PROMPT
from database.db_utils import run_query

llm = load_llm()


def clean_sql(raw: str) -> str:
    """Strip markdown code fences and surrounding whitespace from LLM output."""
    # Remove ```sql ... ``` or ``` ... ``` blocks
    cleaned = re.sub(r"```(?:sql)?\s*", "", raw, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    return cleaned


def generate_sql(user_question: str) -> str:
    prompt = f"""{SYSTEM_PROMPT}

Convert this question to SQL:
{user_question}

Return ONLY the raw SQL query.
"""
    response = llm.invoke(prompt)
    raw_sql = response.content.strip()
    return clean_sql(raw_sql)


def ask_chatbot(user_question: str):
    """
    Returns (sql_query: str, result: DataFrame | dict)
    On SQL execution error, result is a dict with keys 'error' and 'sql'.
    """
    sql_query = generate_sql(user_question)
    result = run_query(sql_query)

    # db_utils returns a string on error — wrap it for structured error handling
    if isinstance(result, str):
        result = {"error": result, "sql": sql_query}

    return sql_query, result