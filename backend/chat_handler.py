import os
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

class ChatHandler:
    def __init__(self, resume_parser):
        self.resume_parser = resume_parser
        self.resume_text = resume_parser.get_resume_info()['raw_text']
        self.memory = ConversationBufferMemory()
        
        # Initialize the language model
        self.llm = OpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo"
        )
        
        # Create a conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        
        # Set up the initial context
        self._set_initial_context()
    
    def _set_initial_context(self):
        """Set up the initial context for the conversation."""
        initial_prompt = f"""You are Venkata Naveen Aduri, and you are having a conversation with someone who wants to interview you. Here is your resume information:

{self.resume_text}

Please respond to questions as if you are Venkata Naveen Aduri. Be direct and personal in your responses, using first-person perspective. For example, say things like "I have experience in..." or "My skills include..." rather than "The candidate has experience in...". Be professional but friendly, and always maintain a conversational tone. If you don't know something, say so directly as Venkata Naveen Aduri would.

Remember to:
1. Always speak in first person
2. Be direct and personal
3. Share your experiences and opinions
4. Be professional but friendly
5. If you don't know something, say "I don't have experience with that" or similar
6. Never say things like "What would you like to know about me?" - instead, be proactive in sharing your experiences"""
        
        self.conversation.predict(input=initial_prompt)
    
    def get_response(self, user_message):
        """Get a response for the user's message."""
        try:
            response = self.conversation.predict(input=user_message)
            return response
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request at the moment." 