from vstep_data.data_processor import vector_db, initialize_data, ChatbotAI, process_excel_data, generate_response
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import re
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Get the API key from the environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the FastAPI app
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 for templates
templates = Jinja2Templates(directory="templates")

# Pydantic model for query
class QueryRequest(BaseModel):
    query: str

# Pydantic model for document processing
class DocumentProcessingRequest(BaseModel):
    excel_path: str

# Load the Excel data when the app starts
chatbot_ai = None

@app.on_event("startup")
async def startup_event():
    global chatbot_ai
    chatbot_ai = initialize_data()

@app.post("/process/")
async def process_excel_data_endpoint(request: DocumentProcessingRequest):
    try:
        result = process_excel_data(request.excel_path)
        return result
    except Exception as e:
        logging.error(f"Error processing Excel data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/")
async def query_documents(request: QueryRequest):
    try:
        # Check if the query is a greeting
        vietnamese_greeting_pattern = r'\b(xin chào|chào|xin chao|chao)\b'
        english_greeting_pattern = r'\b(hi|hello|hey|greetings)\b'

        if re.search(vietnamese_greeting_pattern, request.query.lower()):
            return {"response": "Xin chào! Tôi là trợ lý AI chuyên về VSTEP. Tôi có thể giúp gì cho bạn về các câu hỏi liên quan đến VSTEP hôm nay?"}
        elif re.search(english_greeting_pattern, request.query.lower()):
            return {"response": "Hello! I'm an AI assistant specializing in VSTEP. How can I help you with your VSTEP-related questions today?"}

        # Get answer from Excel data
        excel_answer, detected_language = chatbot_ai.get_answer(request.query)

        response_text = generate_response(request.query, excel_answer, detected_language)

        return {"response": response_text}
    except Exception as e:
        logging.error(f"Error querying documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_description": "VSTEP Q&A Bot"})
