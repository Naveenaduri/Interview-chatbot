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

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Get both explicit and inferred skills from the resume."""
    extracted_skills = chat_handler.extracted_skills
    inferred_skills = chat_handler.inferred_skills
    
    return jsonify({
        'explicit_skills': extracted_skills,
        'inferred_skills': inferred_skills
    })
