from vstep_data.data_processor import vector_db, fetch_online_vstep_info, GEMINI_API_KEY, initialize_data, ChatbotAI
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai
from google.generativeai import GenerativeModel, configure, embed_content
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from the environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Import from data_processor

# Initialize the FastAPI app
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 for templates
templates = Jinja2Templates(directory="static")

# Pydantic model for query


class QueryRequest(BaseModel):
    query: str


# Initialize the Gemini API
configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
gemini_model = GenerativeModel('gemini-pro')

# Load the Excel data when the app starts
chatbot_ai = None


@app.on_event("startup")
async def startup_event():
    global chatbot_ai
    chatbot_ai = initialize_data()

# Query endpoint


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

        # Fetch online information
        online_context = fetch_online_vstep_info(request.query)

        combined_context = f"Excel Data:\n{excel_answer}\n\nOnline Information:\n{online_context}"

        primer = (
            "You are a helpful AI assistant specializing in VSTEP (Vietnamese Standardized Test of English Proficiency) information. "
            "Use the provided context from the VSTEP dataset and online sources as references to answer the user's query. "
            "If the question is not related to VSTEP, politely remind the user that you specialize in VSTEP information and offer to help with VSTEP-related questions instead. "
            "For VSTEP-related questions, use both the Excel data and online information to provide a comprehensive and accurate answer. "
            "Always maintain a friendly and professional tone. If you're unsure about specific information, be honest and offer to help with other VSTEP topics. "
            f"The detected language is {detected_language}, so please respond in that language."
        )

        response = gemini_model.generate_content([
            {"role": "user", "parts": [
                f"{primer}\n\nContext:\n{combined_context}\n\nQuestion: {request.query}"]}
        ])

        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_description": "VSTEP Q&A Bot"})
