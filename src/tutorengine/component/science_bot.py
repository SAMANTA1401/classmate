import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY=os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY

from langchain_google_genai import ChatGoogleGenerativeAI
from src.tutorengine.prompts import ScienceBotPrompt
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate 
from langchain.output_parsers import  PydanticOutputParser 
from src.logger import logging
from src.exception import CustomException
import sys



class ScienceBot:
    def __init__(self):
        self.llm1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.prompttemplate= ScienceBotPrompt.scienceTemplate

    def route(self, state):
        logging.info("Inside ScienceBot")
        try:

            messages =state["messages"]
            context=messages[-1] # last message
            template = self.prompttemplate  

            prompt = PromptTemplate(template=template,
                                        input_variables=[context],
                                        partial_variables={}
                                        )

            chain =  prompt | self.llm1 | StrOutputParser()
        
            response = chain.invoke({"context": context})
        
            return {"messages": [response]}

        except Exception as e:
            raise logging.info(CustomException(e,sys))
        


if __name__ == "__main__":
    router = ScienceBot()
    state = {"messages": ["hello!"]}
    response = router.route(state)
    print(response)











        # parser = PydanticOutputParser(pydantic_object=FieldSelectionParser)
        # prompt = PromptTemplate(template=template,
        #                         input_variables=[question],
        #                         partial_variables={
        #                             "format_instructions" : parser.get_format_instructions()    
        #                         } 
        #                         )
        # chain =  prompt | self.llm1 | parser
        # response = chain.invoke({"question":question,"format_instructions" : parser.get_format_instructions() })
        # return {"messages": [response]}