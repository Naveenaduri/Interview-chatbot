from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
from resume_parser import ResumeParser
from chat_handler import ChatHandler
import spacy
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

mail = Mail(app)

# Load spaCy model for NLP
nlp = spacy.load("en_core_web_sm")

# Initialize resume parser and chat handler
resume_parser = ResumeParser('venkata-aduri.pdf')
chat_handler = ChatHandler(resume_parser)

def extract_skills_from_text(text):
    """Extract skills from text using NLP and pattern matching."""
    # Common technical skills patterns
    technical_skills = [
        r'\b(python|java|c\+\+|javascript|typescript|react|angular|vue|node\.js|express|django|flask|spring|ruby|php|swift|kotlin)\b',
        r'\b(sql|mysql|postgresql|mongodb|redis|oracle|sqlite)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|terraform|ansible|jenkins|git|github|gitlab)\b',
        r'\b(machine learning|deep learning|nlp|computer vision|data science|ai|artificial intelligence)\b',
        r'\b(html|css|sass|less|bootstrap|tailwind|material-ui|jquery)\b',
        r'\b(rest|graphql|api|microservices|soa|websocket|grpc)\b',
        r'\b(linux|unix|windows|macos|ios|android)\b',
        r'\b(agile|scrum|kanban|devops|ci/cd|tdd|bdd)\b'
    ]
    
    # Common soft skills
    soft_skills = [
        r'\b(communication|teamwork|leadership|problem-solving|critical thinking|time management|adaptability|creativity)\b',
        r'\b(collaboration|negotiation|presentation|public speaking|mentoring|coaching|project management)\b'
    ]
    
    # Combine all patterns
    all_patterns = technical_skills + soft_skills
    
    # Extract skills using patterns
    skills = set()
    for pattern in all_patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            skills.add(match.group().capitalize())
    
    # Use spaCy for additional skill extraction
    doc = nlp(text)
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and token.text.lower() not in ['i', 'me', 'my', 'we', 'our']:
            # Check if the word is likely a skill
            if len(token.text) > 2 and not token.is_stop:
                skills.add(token.text.capitalize())
    
    return sorted(list(skills))

@app.route('/api/extract-skills', methods=['POST'])
def extract_skills():
    """Extract skills from the provided text."""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        skills = extract_skills_from_text(text)
        
        return jsonify({
            'skills': skills,
            'count': len(skills)
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to extract skills',
            'details': str(e)
        }), 500

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

@app.route('/api/experience', methods=['GET'])
def get_experience():
    """Get professional experience from the resume."""
    try:
        # Get the resume text from the chat handler
        resume_text = chat_handler.resume_text
        
        # Initialize experience sections
        professional_experience = []
        other_experience = []
        current_experience = None
        
        # Split resume into sections
        sections = resume_text.split('\n\n')
        
        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            # Check if this is a professional experience section
            if any(line.lower().startswith(('professional experience', 'work experience', 'employment history')) for line in lines):
                current_section = professional_experience
            elif any(line.lower().startswith(('other experience', 'additional experience', 'volunteer experience')) for line in lines):
                current_section = other_experience
            else:
                continue
                
            # Process each experience entry
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for new experience entry (usually starts with company name or position)
                if line[0].isupper() and (' at ' in line or ' - ' in line):
                    if current_experience:
                        # Extract skills from the previous experience's description
                        if current_experience.get('description'):
                            skills = extract_skills_from_text(current_experience['description'])
                            current_experience['skills'] = skills
                        current_section.append(current_experience)
                    
                    # Extract position, company, and duration
                    if ' at ' in line:
                        position, rest = line.split(' at ', 1)
                        if ' (' in rest:
                            company, duration = rest.split(' (', 1)
                            duration = duration.rstrip(')')
                        else:
                            company = rest
                            duration = None
                    else:
                        position, rest = line.split(' - ', 1)
                        if ' (' in rest:
                            company, duration = rest.split(' (', 1)
                            duration = duration.rstrip(')')
                        else:
                            company = rest
                            duration = None
                    
                    current_experience = {
                        'position': position.strip(),
                        'company': company.strip(),
                        'duration': duration,
                        'description': '',
                        'skills': []
                    }
                # Collect description text
                elif current_experience:
                    current_experience['description'] += line + ' '
        
        # Add the last experience if exists
        if current_experience:
            if current_experience.get('description'):
                skills = extract_skills_from_text(current_experience['description'])
                current_experience['skills'] = skills
            if current_section == professional_experience:
                professional_experience.append(current_experience)
            else:
                other_experience.append(current_experience)
        
        return jsonify({
            'professional_experience': professional_experience,
            'other_experience': other_experience
        })
        
    except Exception as e:
        print(f"Error in get_experience: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch experience data',
            'details': str(e)
        }), 500

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        email = data.get('email')
        message = data.get('message')
        
        if not email or not message:
            return jsonify({'error': 'Email and message are required'}), 400
            
        msg = Message(
            subject='New Contact Form Submission',
            recipients=[os.getenv('EMAIL_USER')],  # Your email address
            body=f'''
            New message from: {email}
            
            Message:
            {message}
            '''
        )
        
        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({'error': 'Failed to send email'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 