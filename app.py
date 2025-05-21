from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime
from agents.nodes import build_workflow

from langsmith import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize the ChatOpenAI client
llm = ChatOpenAI(
    model="o4-mini-2025-04-16"
)

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Pydantic model for chat request
class ChatMessage(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.post("/chat-message")
async def chat_message(chat_message: ChatMessage):
    request_id = f"req_{int(time.time())}_{hash(chat_message.message)%1000}"
    logger.info(f"[{request_id}] New chat message received: {chat_message.message[:50]}...")
    
    try:
        start_time = time.time()
        logger.info(f"[{request_id}] Sending request to AI model")

        # Get the existing HTML content from page.html
        try:
            with open("page.html", "r") as f:
                existing_html_content = f.read()
        except FileNotFoundError:
            existing_html_content = ""

        ## New step: Figure out the user's intent, and then based on their response, call the appropriate function.
        # Write AI response to page.html
        graph = build_workflow()
        output = graph.invoke({
            "messages": [HumanMessage(content=chat_message.message)],
            "initial_user_message": chat_message.message,
            "existing_html_content": existing_html_content
        })

        langgraph_messages = output.get("messages", [])
        # Convert LangChain message objects to JSON serializable format
        serializable_messages = []
        for msg in langgraph_messages:
            serializable_messages.append({
                "type": msg.__class__.__name__,
                "content": msg.content
            })

        return JSONResponse(content={
            "messages": serializable_messages,
            "request_id": request_id,
        })
        
    except Exception as e:
        logger.error(f"[{request_id}] Error processing message: {str(e)}", exc_info=True)
        return JSONResponse(
            content={
                "message": f"Error: {str(e)}",
                "request_id": request_id
            }, 
            status_code=500
        )
    finally:
        logger.info(f"[{request_id}] Request completed")

@app.get("/chat", response_class=HTMLResponse)
async def chat():
    with open("chat.html") as f:
        return f.read()

@app.get("/page", response_class=HTMLResponse)
async def page():
    with open("page.html") as f:
        return f.read()