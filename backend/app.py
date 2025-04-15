from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from resume_parser import ResumeParser
from chat_handler import ChatHandler

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize resume parser and chat handler
resume_parser = ResumeParser('venkata-aduri.pdf')
chat_handler = ChatHandler(resume_parser)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = chat_handler.get_response(user_message)
    return jsonify({'response': response})

@app.route('/api/resume-info', methods=['GET'])
def get_resume_info():
    info = resume_parser.get_resume_info()
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 