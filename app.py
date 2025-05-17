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
        
        ai_response = llm.invoke([HumanMessage(content=chat_message.message)])
        processing_time = time.time() - start_time
        logger.info(f"[{request_id}] AI response received in {processing_time:.2f} seconds")
        logger.info(f"[{request_id}] Full AI response: {ai_response.content}")
        
        # Write AI response to page.html
        try:
            with open("page.html", "w") as f:
                f.write(ai_response.content)
            logger.info(f"[{request_id}] Successfully wrote AI response to page.html")
        except Exception as write_error:
            logger.error(f"[{request_id}] Error writing to page.html: {str(write_error)}", exc_info=True)
            raise write_error
        
        return JSONResponse(content={
            "message": ai_response.content,
            "request_id": request_id,
            "processing_time": processing_time
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