from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from vstep_data.data_processor import vector_db, initialize_data, ChatbotAI, process_excel_data, generate_response
import re
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Get the API key from the environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Setup Jinja2 for templates
app.template_folder = "templates"
app.static_folder = "static"

# Load the Excel data when the app starts
chatbot_ai = initialize_data()

@app.route("/process/", methods=["POST"])
def process_excel_data_endpoint():
    try:
        data = request.get_json()
        excel_path = data.get('excel_path')
        result = process_excel_data(excel_path)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error processing Excel data: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/query/", methods=["POST"])
def query_documents():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")  # Log received data
        user_query = data.get('query')
        logging.info(f"User query: {user_query}")

        # Check if the query is a greeting
        vietnamese_greeting_pattern = r'\b(xin chào|chào|xin chao|chao)\b'
        english_greeting_pattern = r'\b(hi|hello|hey|greetings)\b'

        if re.search(vietnamese_greeting_pattern, user_query.lower()):
            return jsonify({"response": "Xin chào! Tôi là trợ lý AI chuyên về VSTEP. Tôi có thể giúp gì cho bạn về các câu hỏi liên quan đến VSTEP hôm nay?"})
        elif re.search(english_greeting_pattern, user_query.lower()):
            return jsonify({"response": "Hello! I'm an AI assistant specializing in VSTEP. How can I help you with your VSTEP-related questions today?"})

        # Get answer from Excel data
        excel_answer, detected_language = chatbot_ai.get_answer(user_query)
        logging.info(f"Excel answer: {excel_answer}, Detected language: {detected_language}")

        response_text = generate_response(user_query, excel_answer, detected_language)

        return jsonify({"response": response_text})
    except Exception as e:
        logging.error(f"Error querying documents: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/")
def root():
    return render_template("index.html", app_description="VSTEP Q&A Bot")

if __name__ == "__main__":
    app.run(debug=True)