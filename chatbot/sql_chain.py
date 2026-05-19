from chatbot.llm import load_llm
from chatbot.prompts import SYSTEM_PROMPT
from database.db_utils import run_query

llm = load_llm()

def generate_sql(user_question):

    prompt = f"""
    {SYSTEM_PROMPT}

    Convert this question into SQL:
    {user_question}

    Return ONLY SQL query.
    """

    response = llm.invoke(prompt)

    return response.content.strip()


def ask_chatbot(user_question):

    sql_query = generate_sql(user_question)

    result = run_query(sql_query)

    return sql_query, result