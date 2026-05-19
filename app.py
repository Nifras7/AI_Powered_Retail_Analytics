import streamlit as st

from chatbot.sql_chain import ask_chatbot
from chatbot.response_formatter import format_response

from analytics.charts import sales_chart
from analytics.insights import generate_insights

st.set_page_config(
    page_title="Retail AI Chatbot",
    layout="wide"
)

st.title("AI-Powered Retail Analytics Chatbot")

question = st.text_input(
    "Ask Retail Question"
)

if st.button("Analyze"):

    sql_query, result = ask_chatbot(question)

    st.subheader("Generated SQL")

    st.code(sql_query, language="sql")

    st.subheader("Query Result")

    st.write(format_response(result))

    if hasattr(result, "empty") and not result.empty:

        st.plotly_chart(
            sales_chart(result)
        )

        st.subheader("AI Insights")

        insights = generate_insights(result)

        for insight in insights:
            st.write(f"- {insight}")