# Resume Chatbot

A chatbot application that can answer questions about a candidate based on their resume and GitHub profile. Built with React and Python.

## Features

- Interactive chat interface
- Resume parsing and analysis
- Natural language processing for answering questions
- Modern UI with Material-UI components
- First-person responses as the candidate

## Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn
- OpenAI API key

## Project Structure

```
.
├── backend/
│   ├── app.py              # Flask application
│   ├── chat_handler.py     # Chat logic and OpenAI integration
│   ├── resume_parser.py    # PDF resume parsing
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/            # Static files
│   ├── src/              # React source code
│   └── package.json      # Node.js dependencies
└── venkata-aduri.pdf     # Resume file
```

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd resume-chatbot
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. Create environment file:
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   ```

4. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

1. Start the backend server:
   ```bash
   cd backend
   # Make sure your virtual environment is activated
   python app.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. The chatbot will automatically load your resume information
2. Type your questions in the chat interface
3. The bot will respond as Venkata Naveen Aduri, using first-person perspective
4. You can ask about:
   - Work experience
   - Education
   - Skills
   - Projects
   - And more!

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `FLASK_ENV`: Development environment (development/production)
- `FLASK_APP`: Flask application entry point