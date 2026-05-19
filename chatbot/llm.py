from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def load_llm():
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    return llm