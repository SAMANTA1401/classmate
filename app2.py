from flask import Flask, render_template, request 
from src.logger import logging
from src.exception import CustomException
from IPython.display import display, Markdown
from src.tutorengine.pipeline.master_pipeline import MasterPipeline 
from src.tutorengine.utils import FieldSelectionParser 
from pydantic import BaseModel


app = Flask(__name__)


# Define request model
class ChatRequest(BaseModel):
    prompt: str
    session_id: str = None


@app.route("/")
def index():
    return render_template("masterbot.html")

@app.route("/get", methods = ["POST", "GET"])
def chat():
   
   if request.method == "POST":
        prompt = request.form["msg"]
        inputs = {"messages":[prompt]} 
        chat_history = [f"UserMessage:my name is Shubhankar Samnata, age is 20, study in class 10" f"SystemMessage: hi! I am your classmate"]
        workflow = MasterPipeline(chat_history).workflow()


        for output in workflow.stream(inputs):
                    for key, value in output.items():
                        # Assuming value is the response content we want to stream
                        print(key)
                        print(value)
                        chat_history.extend([f"UserMessage:{value['messages'][0].Question_or_query}",f"SystemMessage:{value['messages'][0].Answer}"])
                        print("chat_history",chat_history)
                        answer_value = value['messages'][0].Answer 
                        print("answer_value", answer_value)
                        response_chunk = str(answer_value)
                        # yield f"data: {response_chunk}\n\n"
                        
    
 

        return str(response_chunk)

if __name__ == '__main__':
    
    app.run(host="0.0.0.0",port=5000,debug= True)