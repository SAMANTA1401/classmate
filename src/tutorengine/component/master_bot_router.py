from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from IPython.display import display, Markdown


import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY=os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"]=GROQ_API_KEY

llm1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# llm2 = ChatGroq(model="gemma2-9b-it")
# llm3 = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
llm4 = ChatGroq(model="llama3-8b-8192")
