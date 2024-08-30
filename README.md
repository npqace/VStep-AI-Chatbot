# VSTEP Chatbot

This is an AI-powered chatbot application specializing in VSTEP (Vietnamese Standardized Test of English Proficiency) information. The chatbot uses a combination of pre-loaded Excel data and real-time online information to provide comprehensive answers to user queries about VSTEP.

## Features

- Responds to user queries about VSTEP in both English and Vietnamese
- Uses a combination of local Excel data and online information for answers
- Powered by Google's Gemini AI model for natural language processing
- FastAPI backend for efficient API handling
- Simple web interface for user interaction

## Prerequisites

- Python 3.7+
- FastAPI
- Pydantic
- Google GenerativeAI
- Pandas
- Scikit-learn
- BeautifulSoup4
- Requests
- python-dotenv
- Qdrant (for vector database)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/vstep-chatbot.git
   cd vstep-chatbot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the root directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. Prepare your VSTEP data:
   Place your Excel file (`Chatbot-VSTEP.xlsx`) in the `vstep_data` directory.

## Usage

1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

2. Open a web browser and navigate to `http://localhost:8000` to access the chatbot interface.

3. Type your VSTEP-related questions in either English or Vietnamese and receive answers from the AI assistant.

## Project Structure

- `main.py`: FastAPI application and main logic
- `vstep_data/data_processor.py`: Data processing and chatbot AI implementation
- `static/`: Directory for static files and HTML templates
- `vstep_data/`: Directory for VSTEP Excel data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.