from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
if os.environ.get("GEMINI_API_KEY"):
    print("API KEY CONNECTED")
else:
    raise ValueError("API KEY NOT FOUND")


def load_llm():
    llm = ChatGoogleGenerativeAI(
        model = "gemini-2.5-flash",
        temperature = 0
    )

    return llm