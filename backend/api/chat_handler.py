import os
import json
import requests
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

class ChatHandler:
    def __init__(self, resume_parser):
        self.resume_parser = resume_parser
        self.resume_text = resume_parser.get_resume_info()['raw_text']
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo"
        )
        
        # Create a custom prompt template that's compatible with the memory system
        self.prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"],
            template=f"""You are Venkata Naveen Aduri, and you are having a conversation with someone who wants to interview you. 
Here is your resume information:

{self.resume_text}

You should respond as if you are Venkata Naveen Aduri, using first-person perspective. Be direct and personal in your responses.

IMPORTANT INSTRUCTIONS:
1. Always speak in first person ("I", "my", "me")
2. Be direct and personal
3. Share your experiences and opinions
4. Be professional but friendly
5. If asked about skills or technologies not explicitly mentioned in your resume:
   - Make reasonable inferences based on your existing experience
   - Connect related technologies to what you do know
   - Be confident but honest about your knowledge
   - If you truly don't know something, say so directly
6. Build upon previous responses to maintain a coherent narrative
7. Never say things like "What would you like to know about me?" - instead, be proactive in sharing your experiences
8. When discussing your GitHub projects, be specific about what you built and the technologies used
9. When discussing skills, always mention relevant projects from your GitHub repositories

Previous conversation:
{{chat_history}}

Human: {{human_input}}
Venkata Naveen Aduri:"""
        )
        
        # Configure memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="human_input",
            output_key="text",
            return_messages=False
        )
        
        # Create a conversation chain with the custom prompt
        self.conversation = ConversationChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True,
            input_key="human_input",
            output_key="text"
        )
        
        # Set up the initial context
        self._set_initial_context()
        
        # Initialize skill graph for inference
        self._initialize_skill_graph()
        
        # Fetch GitHub repositories
        self.github_repos = self._fetch_github_repos("naveenaduri")
        
        # Build a comprehensive skill database from resume and GitHub
        self._build_comprehensive_skill_database()
    
    def _fetch_github_repos(self, username):
        """Fetch repositories from GitHub for the given username."""
        try:
            # Use GitHub API to fetch repositories
            response = requests.get(f"https://api.github.com/users/{username}/repos")
            if response.status_code == 200:
                repos = response.json()
                # Extract relevant information
                repo_info = []
                for repo in repos:
                    repo_info.append({
                        "name": repo.get("name", ""),
                        "description": repo.get("description", ""),
                        "url": repo.get("html_url", ""),
                        "topics": repo.get("topics", []),
                        "language": repo.get("language", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0)
                    })
                return repo_info
            else:
                print(f"Error fetching GitHub repos: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception fetching GitHub repos: {str(e)}")
            return []
    
    def _build_comprehensive_skill_database(self):
        """Build a comprehensive skill database from resume and GitHub repositories."""
        # Initialize the skill database
        self.skill_database = {
            "skills": {},  # Map of skill name to details
            "projects": {}  # Map of project name to skills used
        }
        
        # Extract skills from resume
        resume_skills = self._extract_skills_from_resume()
        for skill in resume_skills:
            self.skill_database["skills"][skill] = {
                "source": "resume",
                "projects": [],
                "confidence": "high"
            }
        
        # Extract skills from GitHub repositories
        for repo in self.github_repos:
            # Add the primary language as a skill
            if repo["language"]:
                lang = repo["language"]
                if lang not in self.skill_database["skills"]:
                    self.skill_database["skills"][lang] = {
                        "source": "github",
                        "projects": [repo["name"]],
                        "confidence": "high"
                    }
                else:
                    self.skill_database["skills"][lang]["projects"].append(repo["name"])
                    if self.skill_database["skills"][lang]["source"] == "resume":
                        self.skill_database["skills"][lang]["source"] = "both"
            
            # Add topics as skills
            for topic in repo["topics"]:
                if topic not in self.skill_database["skills"]:
                    self.skill_database["skills"][topic] = {
                        "source": "github",
                        "projects": [repo["name"]],
                        "confidence": "medium"
                    }
                else:
                    self.skill_database["skills"][topic]["projects"].append(repo["name"])
                    if self.skill_database["skills"][topic]["source"] == "resume":
                        self.skill_database["skills"][topic]["source"] = "both"
            
            # Store project information
            self.skill_database["projects"][repo["name"]] = {
                "description": repo["description"],
                "url": repo["url"],
                "language": repo["language"],
                "topics": repo["topics"]
            }
        
        # Infer additional skills based on the skill graph
        for skill in resume_skills:
            if skill in self.skill_graph:
                for inferred_skill in self.skill_graph[skill]:
                    if inferred_skill not in self.skill_database["skills"]:
                        self.skill_database["skills"][inferred_skill] = {
                            "source": "inferred",
                            "projects": [],
                            "confidence": "low",
                            "inferred_from": skill
                        }
    
    def _set_initial_context(self):
        """Set up the initial context for the conversation."""
        # Store the resume text as a class attribute for later use
        self.resume_text_for_prompt = self.resume_text
        
        # Add initial context to the conversation
        initial_prompt = f"""You are Venkata Naveen Aduri, and you are having a conversation with someone who wants to interview you. Here is your resume information:

{self.resume_text}

Please respond to questions as if you are Venkata Naveen Aduri. Be direct and personal in your responses, using first-person perspective. For example, say things like "I have experience in..." or "My skills include..." rather than "The candidate has experience in...". Be professional but friendly, and always maintain a conversational tone.

When asked about skills or technologies not explicitly mentioned in your resume:
1. Make reasonable inferences based on your existing experience
2. Connect related technologies to what you do know
3. Be confident but honest about your knowledge
4. If you truly don't know something, say so directly

Remember to:
1. Always speak in first person
2. Be direct and personal
3. Share your experiences and opinions
4. Be professional but friendly
5. Build upon previous responses to maintain a coherent narrative
6. Never say things like "What would you like to know about me?" - instead, be proactive in sharing your experiences"""
        
        # Add initial context to the conversation
        self.conversation.predict(human_input=initial_prompt)
    
    def _initialize_skill_graph(self):
        """Initialize a skill graph for making inferences about related technologies."""
        # This is a simplified version - in a real implementation, this would be more comprehensive
        self.skill_graph = {
            "Python": ["Django", "Flask", "FastAPI", "Pandas", "NumPy", "SciPy", "PyTorch", "TensorFlow", "Scikit-learn"],
            "JavaScript": ["React", "Angular", "Vue.js", "Node.js", "Express", "TypeScript", "jQuery"],
            "Java": ["Spring", "Hibernate", "Maven", "Gradle", "JUnit", "Android"],
            "SQL": ["MySQL", "PostgreSQL", "Oracle", "SQL Server", "MongoDB", "Redis"],
            "AWS": ["EC2", "S3", "Lambda", "DynamoDB", "CloudFormation", "CloudWatch"],
            "DevOps": ["Docker", "Kubernetes", "Jenkins", "CI/CD", "Terraform", "Ansible"],
            "Machine Learning": ["TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Pandas", "NumPy"],
            "Web Development": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js", "Node.js"],
            "Data Science": ["Python", "R", "Pandas", "NumPy", "Matplotlib", "Scikit-learn", "TensorFlow"],
            "Cloud Computing": ["AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Serverless"]
        }
        
        # Extract skills from resume text
        self.extracted_skills = self._extract_skills_from_resume()
        
        # Build inferred skills based on the skill graph
        self.inferred_skills = self._build_inferred_skills()
    
    def _extract_skills_from_resume(self):
        """Extract skills from the resume text."""
        # This is a simplified version - in a real implementation, this would use NLP
        skills = []
        for skill in self.skill_graph.keys():
            if skill.lower() in self.resume_text.lower():
                skills.append(skill)
        return skills
    
    def _build_inferred_skills(self):
        """Build a list of inferred skills based on the skill graph."""
        inferred = []
        for skill in self.extracted_skills:
            if skill in self.skill_graph:
                inferred.extend(self.skill_graph[skill])
        return list(set(inferred))  # Remove duplicates
    
    def get_response(self, user_message):
        """Get a response for the user's message."""
        try:
            # Check if the question is about skills or technologies
            if self._is_skill_question(user_message):
                # Enhance the prompt with skill inference information
                enhanced_prompt = self._enhance_prompt_with_skills(user_message)
                user_message = enhanced_prompt
            
            # Check if the question is about GitHub repositories
            if self._is_github_question(user_message):
                # Enhance the prompt with GitHub repository information
                enhanced_prompt = self._enhance_prompt_with_github(user_message)
                user_message = enhanced_prompt
            
            # Get response from the model
            response = self.conversation.predict(human_input=user_message)
            
            return response
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request at the moment."
    
    def _is_skill_question(self, message):
        """Check if the question is about skills or technologies."""
        skill_keywords = ["skill", "technology", "programming", "language", "framework", "tool", "software", "platform", "experience with", "knowledge of", "proficient in", "familiar with", "know", "use", "work with", "expertise", "proficiency"]
        return any(keyword in message.lower() for keyword in skill_keywords)
    
    def _is_github_question(self, message):
        """Check if the question is about GitHub repositories or projects."""
        github_keywords = ["github", "repository", "repo", "project", "code", "programming", "work", "portfolio", "build", "created", "developed"]
        return any(keyword in message.lower() for keyword in github_keywords)
    
    def _enhance_prompt_with_skills(self, message):
        """Enhance the prompt with skill inference information."""
        # Extract potential skills mentioned in the question
        mentioned_skills = []
        for skill in self.skill_database["skills"].keys():
            if skill.lower() in message.lower():
                mentioned_skills.append(skill)
        
        # If no skills are explicitly mentioned, try to infer from the question
        if not mentioned_skills:
            # Check for common technology names in the question
            for skill in self.skill_database["skills"].keys():
                if skill.lower() in message.lower():
                    mentioned_skills.append(skill)
        
        # Add skill information to the prompt
        enhanced_message = message
        if mentioned_skills:
            skill_info = "Here's what I know about the skills you're asking about: "
            
            for skill in mentioned_skills:
                skill_details = self.skill_database["skills"][skill]
                source = skill_details["source"]
                projects = skill_details["projects"]
                
                skill_info += f"\n- {skill}: "
                
                if source == "resume":
                    skill_info += "I have this skill listed on my resume."
                elif source == "github":
                    skill_info += f"I've used this in my GitHub projects: {', '.join(projects)}."
                elif source == "both":
                    skill_info += f"I have this skill listed on my resume and have used it in my GitHub projects: {', '.join(projects)}."
                elif source == "inferred":
                    inferred_from = skill_details.get("inferred_from", "my existing skills")
                    skill_info += f"I can infer knowledge of this based on my experience with {inferred_from}."
            
            enhanced_message = skill_info + "\n\n" + message
        
        return enhanced_message
    
    def _enhance_prompt_with_github(self, message):
        """Enhance the prompt with GitHub repository information."""
        # If we have GitHub repositories, add relevant information
        if self.github_repos:
            # Extract potential repository names mentioned in the question
            mentioned_repos = []
            for repo in self.github_repos:
                if repo["name"].lower() in message.lower():
                    mentioned_repos.append(repo)
            
            # If specific repositories are mentioned, provide details about them
            if mentioned_repos:
                repo_details = "Here are some details about my GitHub repositories that might be relevant: "
                for repo in mentioned_repos:
                    repo_details += f"\n- {repo['name']}: {repo['description']} (written in {repo['language']})"
                
                enhanced_message = repo_details + "\n\n" + message
                return enhanced_message
            
            # If no specific repositories are mentioned but it's a general GitHub question
            elif "github" in message.lower() or "repository" in message.lower() or "project" in message.lower():
                # Get top repositories by stars
                top_repos = sorted(self.github_repos, key=lambda x: x["stars"], reverse=True)[:3]
                repo_summary = "Here are some of my notable GitHub repositories: "
                for repo in top_repos:
                    repo_summary += f"\n- {repo['name']}: {repo['description']} (written in {repo['language']})"
                
                enhanced_message = repo_summary + "\n\n" + message
                return enhanced_message
        
        return message 