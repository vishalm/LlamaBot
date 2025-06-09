from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Ollama imports instead of OpenAI
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
    print("✅ Ollama integration available")
except ImportError:
    print("⚠️ langchain_ollama not available, using direct API calls")
    OLLAMA_AVAILABLE = False

from langchain.schema import HumanMessage
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging
import time
import json
import httpx
from datetime import datetime
from agents.react_agent.nodes import build_workflow

# Uncomment these if you have PostgreSQL setup
# from langgraph.checkpoint.postgres import PostgresSaver
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.base import CheckpointTuple
# from psycopg_pool import ConnectionPool

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

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/assets", StaticFiles(directory="../assets"), name="assets")

# Ollama Configuration
class OllamaConfig:
    MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:latest")
    BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))

# Initialize the Ollama LLM
def get_ollama_llm():
    """Get Ollama LLM instance"""
    if OLLAMA_AVAILABLE:
        return ChatOllama(
            model=OllamaConfig.MODEL,
            base_url=OllamaConfig.BASE_URL,
            temperature=OllamaConfig.TEMPERATURE,
        )
    else:
        return None

# Global LLM instance
llm = get_ollama_llm()

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Pydantic model for chat request
class ChatMessage(BaseModel):
    message: str
    thread_id: str = None  # Optional thread_id parameter
    agent: str = None  # Optional agent parameter

# Application state to hold persistent checkpointer, important for session-based persistence.
app.state.checkpointer = None

def get_or_create_checkpointer():
    """Get persistent checkpointer, creating once if needed"""
    if app.state.checkpointer is None:
        # For now, use MemorySaver. Uncomment PostgreSQL code below if you have it set up
        from langgraph.checkpoint.memory import MemorySaver
        app.state.checkpointer = MemorySaver()
        logger.info("Using MemorySaver for session-based persistence.")
        
        # Uncomment this section if you want PostgreSQL persistence:
        # db_uri = os.getenv("DB_URI")
        # if db_uri:
        #     try:
        #         # Create connection pool and PostgresSaver directly
        #         pool = ConnectionPool(db_uri)
        #         app.state.checkpointer = PostgresSaver(pool)
        #         app.state.checkpointer.setup()
        #         logger.info("Using PostgreSQL persistence.")
        #     except Exception as e:
        #         logger.warning(f"Failed to connect to PostgreSQL: {e}. Using MemorySaver.")
        #         app.state.checkpointer = MemorySaver()
        # else:
        #     logger.info("No DB_URI found. Using MemorySaver for session-based persistence.")
        #     app.state.checkpointer = MemorySaver()
    
    return app.state.checkpointer

@app.get("/", response_class=HTMLResponse)
async def root():
    # Serve the home.html file
    try:
        with open("home.html") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>LlamaBot with Ollama</h1>
                <p>Ollama Model: {}</p>
                <p>Base URL: {}</p>
                <p><a href="/chat">Go to Chat</a></p>
            </body>
        </html>
        """.format(OllamaConfig.MODEL, OllamaConfig.BASE_URL)

@app.get("/health")
async def health_check():
    """Check Ollama connectivity"""
    try:
        if OLLAMA_AVAILABLE and llm:
            # Test with a simple message
            test_response = llm.invoke([HumanMessage(content="Hello")])
            return {
                "status": "healthy",
                "ollama_model": OllamaConfig.MODEL,
                "ollama_url": OllamaConfig.BASE_URL,
                "test_response": str(test_response.content)[:50] + "..."
            }
        else:
            # Test direct API call
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OllamaConfig.BASE_URL}/api/tags")
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "ollama_model": OllamaConfig.MODEL,
                        "ollama_url": OllamaConfig.BASE_URL,
                        "direct_api": True
                    }
                else:
                    return {"status": "unhealthy", "error": "Ollama not responding"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/chat-message")
async def chat_message(chat_message: ChatMessage):
    request_id = f"req_{int(time.time())}_{hash(chat_message.message)%1000}"
    logger.info(f"[{request_id}] New chat message received: {chat_message.message[:50]}...")
    
    # Get the existing HTML content from page.html
    try:
        with open("../page.html", "r") as f:
            existing_html_content = f.read()
    except FileNotFoundError:
        existing_html_content = ""

    # Define a generator function to stream the response
    async def response_generator():
        try:
            logger.info(f"[{request_id}] Starting streaming response with Ollama")

            # Initial response with request ID
            yield json.dumps({
                "type": "start",
                "request_id": request_id,
                "model": OllamaConfig.MODEL
            }) + "\n"

            # Use the provided thread_id or default to "5"
            thread_id = chat_message.thread_id or "5"
            logger.info(f"[{request_id}] Using thread_id: {thread_id}")
            
            # Check if we have LangGraph workflow available
            try:
                checkpointer = get_or_create_checkpointer()
                graph = build_workflow(checkpointer=checkpointer, llm=llm)  # Pass Ollama LLM to workflow
                
                stream = graph.stream({
                    "messages": [HumanMessage(content=chat_message.message)],
                    "initial_user_message": chat_message.message,
                    "existing_html_content": existing_html_content
                    }, 
                    config={"configurable": {"thread_id": thread_id}},
                    stream_mode=["updates", "messages"] # "values" is the third option ( to return the entire state object )
                ) 

                # Track the final state to serialize at the end
                final_state = None

                # Stream each chunk
                for chunk in stream:
                    if chunk is not None:

                        is_this_chunk_an_llm_message = isinstance(chunk, tuple) and len(chunk) == 2 and chunk[0] == 'messages'
                        is_this_chunk_an_update_stream_type = isinstance(chunk, tuple) and len(chunk) == 2 and chunk[0] == 'updates'

                        if is_this_chunk_an_llm_message: ## If this is a message from the LLM. (Known as a 'Messages' Chunk streaming from LangGraph

                            # Get the langgraph_node_info.
                            langgraph_node_info = chunk[1][1] # this is dict object with keys => dict_keys(['langgraph_step', 'langgraph_node', 'langgraph_triggers', 'langgraph_path', 'langgraph_checkpoint_ns', 'checkpoint_ns', 'ls_provider', 'ls_model_name', 'ls_model_type', 'ls_temperature'])
                            
                            # Get the AI message from the LLM.
                            message_from_llm = chunk[1][0] #AIMessageChunk object -> https://python.langchain.com/api_reference/core/messages/langchain_core.messages.ai.AIMessageChunk.html

                            # Handle tuple format (node, value)
                            node, value = chunk
                            if value is not None:
                                # Log the streaming output
                                logger.info(f"[{request_id}] Stream update from {langgraph_node_info['langgraph_node']}: {str(message_from_llm)[:100]}...")

                                # Send streaming update for React frontend
                                yield json.dumps({
                                    "type": "update",
                                    "node": langgraph_node_info['langgraph_node'],
                                    "value": str(message_from_llm.content),  # Convert value to string for safety
                                    "model": OllamaConfig.MODEL
                                }) + "\n"
                        
                        elif is_this_chunk_an_update_stream_type:
                            updated_langgraph_state_object = chunk[1] # Dict object
                            
                            node_step_name = list(chunk[1].keys())[-1] # will be one of the following:'route_initial_user_message', 'respond_naturally', 'design_and_plan', 'write_html_code'
                            
                            node, value = chunk
                            if updated_langgraph_state_object is not None:
                                # Log the streaming output
                                logger.info(f"[{request_id}] Stream update from {node}: {str(value)[:100]}...")

                                # Store final state for the final response
                                if 'messages' in updated_langgraph_state_object:
                                    final_state = updated_langgraph_state_object

                        else:
                            # Handle other formats or just log
                            logger.info(f"[{request_id}] Received chunk in unknown format: {type(chunk)}")
                            
            except Exception as workflow_error:
                logger.warning(f"[{request_id}] Workflow error, falling back to direct Ollama call: {workflow_error}")
                
                # Fallback to direct Ollama API call
                if OLLAMA_AVAILABLE and llm:
                    response = llm.invoke([HumanMessage(content=chat_message.message)])
                    yield json.dumps({
                        "type": "update",
                        "node": "direct_ollama",
                        "value": response.content,
                        "model": OllamaConfig.MODEL
                    }) + "\n"
                    
                    final_state = {
                        "messages": [
                            {"role": "user", "content": chat_message.message},
                            {"role": "assistant", "content": response.content}
                        ]
                    }
                else:
                    # Direct HTTP call to Ollama API
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        ollama_request = {
                            "model": OllamaConfig.MODEL,
                            "messages": [
                                {"role": "user", "content": chat_message.message}
                            ],
                            "stream": False
                        }
                        
                        response = await client.post(
                            f"{OllamaConfig.BASE_URL}/api/chat",
                            json=ollama_request
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            content = result["message"]["content"]
                            
                            yield json.dumps({
                                "type": "update",
                                "node": "direct_api",
                                "value": content,
                                "model": OllamaConfig.MODEL
                            }) + "\n"
                            
                            final_state = {
                                "messages": [
                                    {"role": "user", "content": chat_message.message},
                                    {"role": "assistant", "content": content}
                                ]
                            }
                        else:
                            raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            logger.error(f"[{request_id}] Error in stream: {str(e)}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "error": str(e),
                "request_id": request_id
            }) + "\n"
        finally:
            logger.info(f"[{request_id}] Stream completed")
            # Send final update with complete messages
            yield json.dumps({
                "type": "final",
                "node": "final",
                "value": "final",
                "messages": final_state.get("messages", []) if final_state else [],
                "model": OllamaConfig.MODEL
            }) + "\n"

    # Return a streaming response
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )

@app.get("/chat", response_class=HTMLResponse)
async def chat():
    try:
        with open("chat.html") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>Chat with Ollama</h1>
                <p>Model: {}</p>
                <form id="chatForm">
                    <input type="text" id="messageInput" placeholder="Type your message..." style="width: 70%;">
                    <button type="submit">Send</button>
                </form>
                <div id="messages"></div>
                <script>
                    document.getElementById('chatForm').addEventListener('submit', async (e) => {{
                        e.preventDefault();
                        const message = document.getElementById('messageInput').value;
                        if (!message) return;
                        
                        const response = await fetch('/chat-message', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{message: message}})
                        }});
                        
                        const reader = response.body.getReader();
                        const messagesDiv = document.getElementById('messages');
                        messagesDiv.innerHTML += '<p><strong>You:</strong> ' + message + '</p>';
                        
                        let assistantMessage = '<p><strong>Assistant:</strong> ';
                        
                        while (true) {{
                            const {{done, value}} = await reader.read();
                            if (done) break;
                            
                            const text = new TextDecoder().decode(value);
                            const lines = text.split('\\n');
                            
                            for (const line of lines) {{
                                if (line.trim()) {{
                                    try {{
                                        const data = JSON.parse(line);
                                        if (data.type === 'update' && data.value) {{
                                            assistantMessage += data.value;
                                        }}
                                    }} catch (e) {{}}
                                }}
                            }}
                        }}
                        
                        assistantMessage += '</p>';
                        messagesDiv.innerHTML += assistantMessage;
                        document.getElementById('messageInput').value = '';
                    }});
                </script>
            </body>
        </html>
        """.format(OllamaConfig.MODEL)

@app.get("/page", response_class=HTMLResponse)
async def page():
    try:
        with open("../page.html") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Page not found</h1></body></html>"
    
@app.get("/conversations", response_class=HTMLResponse)
async def conversations():
    try:
        with open("conversations.html") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Conversations page not found</h1></body></html>"

@app.get("/threads", response_class=JSONResponse)
async def threads():
    try:
        checkpointer = get_or_create_checkpointer()
        config = {}
        checkpoint_generator = checkpointer.list(config=config)
        all_checkpoints = list(checkpoint_generator) #convert to list
        
        # reduce only to the unique thread_ids  
        unique_thread_ids = list(set([checkpoint[0]["configurable"]["thread_id"] for checkpoint in all_checkpoints]))
        state_history = []
        for thread_id in unique_thread_ids:
            graph = build_workflow(checkpointer=checkpointer, llm=llm)
            config = {"configurable": {"thread_id": thread_id}}
            state_history.append({"thread_id": thread_id, "state": graph.get_state(config=config)})
        return state_history
    except Exception as e:
        logger.error(f"Error getting threads: {e}")
        return {"error": str(e)}

@app.get("/chat-history/{thread_id}")
async def chat_history(thread_id: str):
    try:
        checkpointer = get_or_create_checkpointer()
        graph = build_workflow(checkpointer=checkpointer, llm=llm)
        config = {"configurable": {"thread_id": thread_id}}
        state_history = graph.get_state(config=config)
        print(state_history)
        return state_history
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return {"error": str(e)}

@app.get("/available-agents", response_class=JSONResponse)
async def available_agents():
    try:
        # map from langgraph.json to a list of agent names
        with open("../langgraph.json", "r") as f:
            langgraph_json = json.load(f)
        return {"agents": list(langgraph_json["graphs"].keys())}
    except FileNotFoundError:
        return {"agents": [], "error": "langgraph.json not found"}

@app.get("/models")
async def list_models():
    """List available Ollama models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OllamaConfig.BASE_URL}/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return {
                    "provider": "ollama",
                    "models": models,
                    "current": OllamaConfig.MODEL,
                    "base_url": OllamaConfig.BASE_URL
                }
            else:
                return {
                    "error": "Failed to fetch models from Ollama",
                    "current": OllamaConfig.MODEL
                }
                
    except Exception as e:
        return {
            "error": str(e),
            "current": OllamaConfig.MODEL
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)