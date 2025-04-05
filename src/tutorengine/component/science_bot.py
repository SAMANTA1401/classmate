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
from src.tutorengine.utils import FieldSelectionParser 
from src.tutorengine.utils import ContentSelectorParser


class ScienceBot:
    def __init__(self):
        self.llm1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.prompttemplate= ScienceBotPrompt.scienceTemplate

    def route(self, state):
        logging.info("Inside ScienceBot")
        try:
            logging.info("state",state)
            print("state", state)
            print("state field", state["messages"][0].Field_study)
            messages =state["messages"]
            context=messages[-1] # last message
            template = self.prompttemplate  
            parser3 = PydanticOutputParser(pydantic_object=ContentSelectorParser)
            prompt = PromptTemplate(template=template,
                                        input_variables=[context],
                                        partial_variables={ "format_instructions" : parser3.get_format_instructions()    }
                                        )

            chain =  prompt | self.llm1 | parser3
        
            response = chain.invoke({"context": context})
            print("response", response)

            logging.info("Response from ScienceBot")

            logging.info("field study",state["messages"][0].Field_study)

            

            final_response = ContentSelectorParser(
                Answer=response.Answer,
                Content = response.Content
            )  
        
            return {"messages": [final_response]}

        except Exception as e:
            raise logging.info(CustomException(e,sys))
        


if __name__ == "__main__":
    router = ScienceBot()
    state = {'messages': [FieldSelectionParser(Field_study=None, Subject=None, Chapter=None, Topic='quantum entanglemeent',
                                            Difficulty_level='N/A', Question_or_query='Tell me about quantum entanglement',
                                              Answer="That's a fascinating topic! Quantum entanglement is a phenomenon in which two or more particles become correlated in such a way that the state of one particle cannot be described independently of the others, even when they are not .That is a fascinating topic! Quantum entanglement is a phenomenon in which two or more particles become correlated in such a way that the state of one particle cannot be described independently of the others, even when they arch a way that the state of one particle cannot be described independently of the others, even when they are separated by large distances. This means that the information about the state of one particle is instantly transported to the other particles, regardless of the distance between them. It is a fundamental conceptly transported to the other particles, regardless of the distance between them. It is a fundamental concept in quantum mechanics and has been experimentally verified in various systems.", 
                                              Content=None)]}
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