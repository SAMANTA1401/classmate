from src.logger import logging
from src.exception import CustomException
from IPython.display import display, Markdown
from src.tutorengine.pipeline.master_pipeline import MasterPipeline
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uuid
from pydantic import BaseModel 
import sys  
from src.tutorengine.utils import FieldSelectionParser

# chat_history = [f"UserMessage:my name is Shubhankar Samnata, age is 20, study in class 10" f"SystemMessage: hi! I am your classmate"]


app = FastAPI()

# workflow = MasterPipeline(chat_history).workflow()
# # print(app.stream(inputs)) # generator object 

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class ChatRequest(BaseModel):
    prompt: str
    session_id: str = None



sessions = {}

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        prompt = chat_request.prompt
        session_id = chat_request.session_id or str(uuid.uuid4())

        # Initialize session if it doesn't exist
        if session_id not in sessions:
            sessions[session_id] = [f"UserMessage:my name is Shubhankar Samnata, age is 20, study in class 10" f"SystemMessage: hi! I am your classmate"]


        # Add user message to session history
        chat_history = sessions[session_id]
        # chat_history.append({"role": "user", "content": prompt})
        try:
            # Create LangGraph workflow
            workflow = MasterPipeline(chat_history).workflow()
            
            # Prepare inputs for the workflow
            inputs = {"messages": [prompt]}
        except Exception as e:
            raise logging.info(CustomException(e, sys))
        
        async def stream_response():
            try:
                # Stream the workflow output
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
                        yield f"data: {response_chunk}\n\n"
                        await asyncio.sleep(0.1)  # Small delay to simulate streaming
                
                # Add final response to session history
                # final_response = "Workflow completed"
                # yield f"data: {final_response}\n\n"
            except Exception as e:
                raise logging.info(CustomException(e, sys))

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={"X-Session-ID": session_id}
        )
    
    except Exception as e:
        logging.info(CustomException(e,sys))
        

@app.get("/history")
async def get_history(request: Request):
    session_id = request.query_params.get("session_id")
    if session_id and session_id in sessions:
        return {"history": sessions[session_id]}
    return {"history": []}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

