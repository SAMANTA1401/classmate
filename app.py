from src.logger import logging
from src.exception import CustomException
from IPython.display import display, Markdown
from src.tutorengine.pipeline.master_pipeline import MasterPipeline
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uuid

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

sessions = {}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    session_id = body.get("session_id")

    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append({"role": "user", "content": prompt})

    async def stream_response():
        for i in range(5):
            await asyncio.sleep(1)
            response = f"Streamed response chunk {i+1} for prompt: {prompt}"
            yield f"data: {response}\n\n"

        sessions[session_id].append({"role": "assistant", "content": response})

    return StreamingResponse(stream_response(), media_type="text/event-stream")




# inputs = {"messages": ["Tell me about quantum entanglement"]}

# for output in app.stream(inputs):
#     # stream() yields dictionaries with output keyed by node name
#     for key, value in output.items():
#         print(f"Output from node '{key}':")
#         print("---")
#         print(value)
#     print("\n---\n")




