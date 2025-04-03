from langchain_community.utilities import GoogleSerperAPIWrapper
import json
import requests
import os
from src.exception import CustomException
from src.logger import logging

from dotenv import load_dotenv
import sys
load_dotenv()

os.environ["SERPER_API_KEY"] = os.environ["SERPER_API_KEY"]
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"]=GROQ_API_KEY

from src.tutorengine.prompts import MasterSearchPrompt
from langchain.prompts import PromptTemplate
from src.tutorengine.utils import SearchAnswer 
from langchain.output_parsers import PydanticOutputParser 
from langchain_groq import ChatGroq





class SearchToolMasterBot:
    def __init__(self,llm4):
        self.url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "Content-Type": "application/json"
        }
        self.llm4 = ChatGroq(model="llama3-8b-8192")

    def run(self, query):
        logging.info(" query running...")
        try:
            payload = json.dumps({"q": query, "num": 5})
            result = requests.request("POST", self.url, headers=self.headers, data=payload)
            
            search_data = json.loads(result.text)
            snippets = [result.get("snippet", "") for result in search_data.get("organic", [])]
            context = "\n".join(snippets)
            
            return context
        
        except Exception as e:
            raise logging.info(CustomException(e,sys))
        
        
    def master_search(self,query):
        logging.info("Searching for the query: {}".format(query))
        try:
            context =self.run(query)
            parser2 = PydanticOutputParser(pydantic_object=SearchAnswer)
            
            prompt = PromptTemplate(
                template = MasterSearchPrompt.searchTemplate,
                input_variables=[context, query],
                partial_variables={"format_instructions": parser2.get_format_instructions()}
                )
            
            chain = prompt | self.llm4 | parser2
            search_response = chain.invoke({"context":context , "question":query, "format_instructions":parser2.get_format_instructions()})
        
            return search_response
        
        except Exception as e:
            raise logging.info(CustomException(e,sys))