from flask import Flask, render_template, request 
from src.logger import logging
from src.exception import CustomException
from IPython.display import display, Markdown
from src.tutorengine.pipeline.master_pipeline import MasterPipeline 
from src.tutorengine.utils import FieldSelectionParser 
from src.tutorengine.utils import ContentSelectorParser
from pydantic import BaseModel
import json

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
                # print(value)
                chat_history.extend([f"UserMessage:{value['messages'][0].Question_or_query}",f"SystemMessage:{value['messages'][0].Answer}"])
                # print("chat_history",chat_history)
                answer_value = value['messages'][0].Answer
                content_value = value['messages'][0].Content 
                # print("answer_value", answer_value)
                # print("content_value", content_value)
                if content_value:
                    response_chunk = {"answer": answer_value, "content": content_value}
                    print(response_chunk)
                else:
                    response_chunk = {"answer": answer_value, "content": None}
                    print(response_chunk)

                # Instead of str(), use json.dumps() to create a JSON string
                json_output = json.dumps(response_chunk)
                print("JSON Output:", json_output) # Debugging - This is what JS will receive
                # yield f"data: {response_chunk}\n\n"       
        return  json_output


# @app.route("/get", methods = ["POST", "GET"])
# def playboard():
#      if request.method


if __name__ == '__main__':
    
    app.run(host="0.0.0.0",port=5000,debug= True)