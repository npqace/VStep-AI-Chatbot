import pandas as pd
from tqdm.auto import tqdm
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import google.generativeai as genai
from google.generativeai import configure, embed_content
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from the environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini API
configure(api_key=GEMINI_API_KEY)

# Initialize the Qdrant client
vector_db = QdrantClient(":memory:")  # In-memory instance for testing


class ChatbotAI:
    def __init__(self, excel_path):
        self.df_english = pd.read_excel(excel_path, sheet_name=0)
        self.df_vietnamese = pd.read_excel(excel_path, sheet_name=1)
        self.vectorizer_english = TfidfVectorizer()
        self.vectorizer_vietnamese = TfidfVectorizer()
        self.question_vectors_english = self.vectorizer_english.fit_transform(
            self.df_english['Question'])
        self.question_vectors_vietnamese = self.vectorizer_vietnamese.fit_transform(
            self.df_vietnamese['Question'])

    def detect_language(self, text):
        # Simple language detection based on character set
        vietnamese_chars = set(
            'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ')
        if any(char.lower() in vietnamese_chars for char in text):
            return 'vietnamese'
        return 'english'

    def find_most_similar_question(self, user_question):
        language = self.detect_language(user_question)
        if language == 'english':
            df = self.df_english
            vectorizer = self.vectorizer_english
            question_vectors = self.question_vectors_english
        else:
            df = self.df_vietnamese
            vectorizer = self.vectorizer_vietnamese
            question_vectors = self.question_vectors_vietnamese

        user_question_vector = vectorizer.transform([user_question])
        similarities = cosine_similarity(
            user_question_vector, question_vectors)
        most_similar_idx = similarities.argmax()
        return df.iloc[most_similar_idx], language

    def get_answer(self, user_question):
        most_similar_question, language = self.find_most_similar_question(
            user_question)
        return most_similar_question['Answer'], language


def create_collection():
    vector_db.create_collection(
        collection_name="vstep_data_collection",
        # Gemini embeddings are 768-dimensional
        vectors_config=VectorParams(size=768, distance=Distance.DOT),
    )


def fetch_online_vstep_info(query):
    search_url = f"https://www.google.com/search?q=VSTEP+{query.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract snippets from search results
        snippets = soup.find_all('div', class_='g')
        relevant_text = []

        for snippet in snippets[:3]:  # Consider top 3 results
            title = snippet.find('h3', class_='r')
            content = snippet.find('div', class_='s')
            if title and content:
                relevant_text.append(
                    f"{title.get_text()} - {content.get_text()}")

        return "\n".join(relevant_text)
    except Exception as e:
        print(f"Error fetching online information: {e}")
        return ""


def initialize_data():
    create_collection()
    # Replace with your Excel file path
    excel_file_path = "vstep_data/Chatbot-VSTEP.xlsx"
    chatbot_ai = ChatbotAI(excel_file_path)
    return chatbot_ai
