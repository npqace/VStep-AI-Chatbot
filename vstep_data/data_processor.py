import pandas as pd
from tqdm.auto import tqdm
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import google.generativeai as genai
from google.generativeai import GenerativeModel, configure, embed_content
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv
from time import sleep
import re

# Load environment variables
load_dotenv()

# Get the API key from the environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini API
configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
gemini_model = GenerativeModel('gemini-pro')

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

def initialize_data():
    create_collection()
    # Replace with your Excel file path
    excel_file_path = "vstep_data/Chatbot-VSTEP.xlsx"
    chatbot_ai = ChatbotAI(excel_file_path)
    return chatbot_ai

def process_excel_data(excel_path):
    df_english = pd.read_excel(excel_path, sheet_name=0)
    df_vietnamese = pd.read_excel(excel_path, sheet_name=1)

    data = []
    for idx, row in df_english.iterrows():
        data.append({
            'id': str(uuid4()),
            'text': row['Question'],
            'answer': row['Answer'],
            'language': 'english'
        })

    for idx, row in df_vietnamese.iterrows():
        data.append({
            'id': str(uuid4()),
            'text': row['Question'],
            'answer': row['Answer'],
            'language': 'vietnamese'
        })

    batch_size = 100
    for i in tqdm(range(0, len(data), batch_size)):
        i_end = min(len(data), i + batch_size)
        meta_batch = data[i:i_end]
        ids_batch = [x['id'] for x in meta_batch]
        texts = [x['text'] for x in meta_batch]

        try:
            res = genai.embed_content(texts)
        except:
            done = False
            while not done:
                sleep(5)
                try:
                    res = genai.embed_content(texts)
                    done = True
                except:
                    pass

        embeds = [record.embedding for record in res.data]
        meta_batch = [{'text': x['text'], 'answer': x['answer'], 'language': x['language']} for x in meta_batch]
        list_batch = list(zip(ids_batch, embeds, meta_batch))
        points_list = [PointStruct(id=p[0], vector=p[1], payload=p[2]) for p in list_batch]

        vector_db.upsert(
            collection_name="vstep_data_collection",
            wait=True,
            points=points_list
        )

    return {"message": "Excel data processed successfully"}

def generate_response(query, context, detected_language):
    primer = (
        "You are a helpful AI assistant specializing in VSTEP (Vietnamese Standardized Test of English Proficiency) information. "
        "Use the provided context from the VSTEP dataset to answer the user's query. "
        "If the question is not related to VSTEP, politely remind the user that you specialize in VSTEP information and offer to help with VSTEP-related questions instead. "
        "For VSTEP-related questions, use the Excel data to provide a comprehensive and accurate answer. "
        "Always maintain a friendly and professional tone. If you're unsure about specific information, simply say you don't know. "
        "Format your response with proper paragraphs and use numbered or bulleted lists where appropriate. "
        f"The detected language is {detected_language}, so please respond in that language."
    )

    response = gemini_model.generate_content([
        {"role": "user", "parts": [
            f"{primer}\n\nContext:\n{context}\n\nQuestion: {query}"]}
    ])

    # Process the response to ensure proper formatting
    processed_response = response.text.replace('\n', '<br>')
    processed_response = processed_response.replace('•', '<br>•')
    processed_response = re.sub(r'(\d+)\.\s', r'<br>\1. ', processed_response)

    return processed_response
