import PyPDF2
import os

class ResumeParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.resume_text = self._extract_text()
        
    def _extract_text(self):
        """Extract text from the PDF file."""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return ''
    
    def get_resume_info(self):
        """Return structured information about the resume."""
        return {
            'raw_text': self.resume_text,
            'file_name': os.path.basename(self.pdf_path)
        } 