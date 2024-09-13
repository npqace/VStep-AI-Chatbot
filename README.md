# VSTEP Q&A Bot

VSTEP Q&A Bot is a Flask-based web application that provides answers to questions related to the Vietnamese Standardized Test of English Proficiency (VSTEP). It uses natural language processing and machine learning techniques to understand user queries and provide relevant responses based on a pre-processed dataset.

## Features

- Web interface for user interactions
- Support for both English and Vietnamese languages
- Automatic language detection
- Integration with Google's Gemini AI for enhanced response generation
- Excel data processing for maintaining the question-answer dataset

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/npqace/VStep-AI-Chatbot.git
   cd VStep-AI-Chatbot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. Prepare your Excel data:
   Place your VSTEP Q&A Excel file in the `vstep_data` folder and name it `Chatbot-VSTEP.xlsx`.

5. Run the application:
   ```
   python main.py
   ```

6. Access the web interface at `http://localhost:5000`

## Usage

1. Open the web interface in your browser.
2. Type your VSTEP-related question in either English or Vietnamese.
3. The bot will process your query and provide a relevant answer based on the pre-processed dataset.

## Project Structure

- `main.py`: The main Flask application file
- `data_processor.py`: Contains data processing and AI logic
- `templates/`: HTML templates for the web interface
- `static/`: Static files (CSS, JavaScript) for the web interface
- `vstep_data/`: Folder containing the Excel dataset

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.