from langgraph.graph import Graph
from langgraph.graph import StateGraph,END
from src.tutorengine.utils import AgentState , BaseMessage
from src.tutorengine.component.master_bot_router import MasterBotRouter
from src.tutorengine.component.science_bot import ScienceBot
from src.logger import logging
from src.exception import CustomException
import sys



# Creating an initial state
state: AgentState = {"messages": [BaseMessage("Hello!")]}

class MasterPipeline:
    def __init__(self):
        pass


    def router(self,state):
        logging.info("Router")
        try:
            messages = state["messages"]
            last_message = messages[-1]
            if "Field_study=Science" in last_message:
                return "Science"
            else:
                return "end"
        except Exception as e:
            logging.info(CustomException(e,sys))
    

    def workflow(self):
        logging.info("Starting the workflow")

        try:
            workflow_master = StateGraph(AgentState) ### StateGraph with AgentState

            workflow_master.add_node("masterbot",MasterBotRouter().route) ### Adding the master bot
            workflow_master.add_node("sciencebot", ScienceBot().route) ### Adding the science bot

            workflow_master.set_entry_point("masterbot")

            workflow_master.add_conditional_edges(
                "agent",
                self.router,
                {
                    "Science": "sciencebot",
                    "end" : END
                }
            )

            workflow_master.add_edge("sciencebot", END)
            app = workflow_master.compile()
            return app

        except Exception as e:
            logging.info(CustomException(e, sys))

if __name__ == "__main__":
    app = MasterPipeline().workflow()

    inputs = {"messages": ["Tell me about quantum entanglement"]}
    for output in app.stream(inputs):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")