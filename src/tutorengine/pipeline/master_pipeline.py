from langgraph.graph import Graph
from langgraph.graph import StateGraph,END
from src.tutorengine.utils import AgentState , BaseMessage
from src.tutorengine.component.master_bot_router import MasterBotRouter
from src.tutorengine.component.science_bot import ScienceBot




# Creating an initial state
state: AgentState = {"messages": [BaseMessage("Hello!")]}


# create class

def router(state):
    messages = state["messages"]
    last_message = messages[-1]
    if "Field_study=Science" in last_message:
        return "Science"
    else:
        return "end"

workflow_master = StateGraph(AgentState) ### StateGraph with AgentState

workflow_master.add_node("masterbot",MasterBotRouter().route) ### Adding the master bot
workflow_master.add_node("sciencebot", ScienceBot().route) ### Adding the science bot

workflow_master.set_entry_point("masterbot")

workflow_master.add_conditional_edges(
    "agent",
    router,
    {
        "Science": "sciencebot",
        "end" : END
    }
)


workflow_master.add_edge("sciencebot", END)


app = workflow_master.compile()


inputs = {"messages": ["Tell me about quantum entanglement"]}
for output in app4.stream(inputs):
    # stream() yields dictionaries with output keyed by node name
    for key, value in output.items():
        print(f"Output from node '{key}':")
        print("---")
        print(value)
    print("\n---\n")