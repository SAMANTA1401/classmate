from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from IPython.display import display, Markdown
from src.tutorengine.prompts import MasterBotPrompt 
from langchain.prompts import PromptTemplate 
from langchain.output_parsers import PydanticOutputParser 
from src.tutorengine.utils import FieldSelectionParser
from src.tutorengine.search_tools import SearchToolMasterBot
from src.exception import CustomException
from src.logger import logging

import os
from dotenv import load_dotenv
import sys
load_dotenv()

# GOOGLE_API_KEY=os.getenv("GEMINI_API_KEY")
# os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"]=GROQ_API_KEY

# llm1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# llm2 = ChatGroq(model="gemma2-9b-it")
# llm3 = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
# llm4 = ChatGroq(model="llama3-8b-8192")


class MasterBotRouter:
    def __init__(self, chat_history:list ):
        self.llm4 = ChatGroq(model="llama3-8b-8192")
        self.chat_history = chat_history
        self.prompttemplate= MasterBotPrompt.masterTemplate

    def route(self, state):
        logging.info("MasterBotRouter is routing the request")
        try:
        
            messages =state["messages"]
            question=messages[-1] # last message
            
            chat_history_str = " "
            chat_history_str = "\n".join(self.chat_history)
            
            template = self.prompttemplate
            parser = PydanticOutputParser(pydantic_object=FieldSelectionParser)
            
            prompt = PromptTemplate(template=template,
                                    input_variables=[chat_history_str, question],
                                    partial_variables={
                                        "format_instructions" : parser.get_format_instructions()    
                                    } 
                                    )
            chain =  prompt | self.llm4 | parser
            
            response = chain.invoke({"chat_history":chat_history_str,"question":question,"format_instructions" : parser.get_format_instructions() })
        
            searchresults = None
        
            if response.Answer == "I’m not aware, search needed":
                search = SearchToolMasterBot.master_search(question=str(question))
                searchresults = f"Hi, I looked it up and what I found: {search.extracted_result}"
                # Update the response with search result

            # Update response based on whether search was performed
            final_response = FieldSelectionParser(
                Field_study=response.Field_study,
                Subject=response.Subject,
                Chapter=response.Chapter,
                Topic=response.Topic,
                Difficulty_level=response.Difficulty_level,
                Question_or_query=response.Question_or_query,
                Answer=searchresults if searchresults else response.Answer
            )   
            
            self.chat_history.extend([f"UserMessage:{final_response.Question_or_query}",f"SystemMessage:{final_response.Answer}"])
            
            logging.info("MasterBotRouter is routing the request completed")

            return {"messages": [final_response]}

    
        except Exception as e:
            raise logging.info(CustomException(e,sys))



if __name__ == "__main__":
    ################################
    user_name = "Shubhankar Samnata"
    age = 20
    standard_name = "class 10"
    bot_name = "classmate"
    chat_history = [f"UserMessage:my name is {user_name}, age is {age}, study in {standard_name}" f"SystemMessage: hi! I am your {bot_name}"]
    #################################

    router = MasterBotRouter(chat_history)
    state = {"messages":["hello!"]}
    response = router.route(state)
    print(response)
