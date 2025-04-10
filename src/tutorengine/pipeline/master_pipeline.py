from langgraph.graph import Graph
from langgraph.graph import StateGraph, END
from src.tutorengine.utils import AgentState , BaseMessage
from src.tutorengine.component.master_bot_router import MasterBotRouter
from src.tutorengine.component.science_bot import ScienceBot
from src.logger import logging
from src.exception import CustomException
import sys 
from src.tutorengine.component.summary_bot import SummaryBot



# Creating an initial state
state: AgentState = {"messages": [BaseMessage("Hello!")]}

class MasterPipeline:
    def __init__(self, chat_history:list, filename:str):
        self.chat_history = chat_history
        self.filename = filename

    def router(self,state):
        logging.info("Router initiate")
        try:
            messages = state["messages"]
            last_message = messages[-1]
            if last_message.Field_study == 'science':
            # if "Field_study='science'" in last_message:
                logging.info("Router is routing to science bot")
                return "Science"
            elif last_message.Field_study == 'document_upload':
                logging.info("Router is routing to summary bot")
                return "Summary"
            else:
                return "end"
        except Exception as e:
            logging.info(CustomException(e,sys))
    

    def workflow(self):
        logging.info("Starting the workflow")

        try:
            workflow_master = StateGraph(AgentState) ### StateGraph with AgentState

            workflow_master.add_node("masterbot",MasterBotRouter(chat_history=self.chat_history).route) ### Adding the master bot
            workflow_master.add_node("sciencebot", ScienceBot().route) ### Adding the science bot
            workflow_master.add_node("summarybot", SummaryBot(filename=self.filename).retriever)

            workflow_master.set_entry_point("masterbot")

            workflow_master.add_conditional_edges(
                "masterbot",
                self.router,
                {
                    "Science": "sciencebot",
                    "Summary": "summarybot",
                    "end" : END
                }
            )

            workflow_master.add_edge("sciencebot", END)
            workflow_master.add_edge("summarybot", END)
            app = workflow_master.compile()

            logging.info("Workflow compiled successfully")

            return app

        except Exception as e:
            logging.info(CustomException(e, sys))

if __name__ == "__main__":
    filename = "khanra.pdf"
    chat_history = [f"UserMessage:my name is Shubhankar Samnata, age is 20, study in class 10" f"SystemMessage: hi! I am your classmate"]
    app = MasterPipeline(chat_history,filename).workflow()

    inputs = {"messages": ["Tell me about quantum entanglement"]}

    # print(app.stream(inputs)) # generator object 


    for output in app.stream(inputs):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")