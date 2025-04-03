from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from IPython.display import display, Markdown
from src.tutorengine.prompts import MasterBotPrompt

import os
from dotenv import load_dotenv
load_dotenv()

# GOOGLE_API_KEY=os.getenv("GEMINI_API_KEY")
# os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"]=GROQ_API_KEY

# llm1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# llm2 = ChatGroq(model="gemma2-9b-it")
# llm3 = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
# llm4 = ChatGroq(model="llama3-8b-8192")

################################
user_name = "Shubhankar Samnata"
age = 20
standard_name = "class 10"
bot_name = "classmate"
chat_history = [f"UserMessage:my name is {user_name}, age is {age}, study in {standard_name}" f"SystemMessage: hi! I am your {bot_name}"]
#################################


class MasterBotRouter:
    def __init__(self, chat_history:list ):
        self.llm4 = ChatGroq(model="llama3-8b-8192")
        self.chat_history = chat_history
        self.prompt = MasterBotPrompt.masterTemplate

    def route(self, prompt):
        
        
        
        pass         

    def display(self, prompt):
        response = self.llm.invoke(prompt)
        display(Markdown(response.content))
