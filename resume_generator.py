import os

import tempfile

from fpdf import FPDF

import googleapiclient.discovery

from google.oauth2 import service_account

from googleapiclient.errors import HttpError

import json



class ResumeGenerator:

    def __init__(self, api_key):

        self.api_key = api_key

        

    def enhance_with_ai(self, content, document_type):

        """Use Google AI to enhance the content based on document type"""

        try:

            # This is a placeholder for the actual Google API call

            # In a real implementation, you would call the appropriate Google AI API

            # For now, we'll just return the original content with some basic enhancements

            

            enhanced_content = f"Professionally formatted {document_type}: {content}"

            return enhanced_content

        except Exception as e:

            print(f"Error enhancing content with AI: {e}")

            return content

    

    def generate_resume(self, name, email, document_type, experience, education, skills, about):

        """Generate a resume PDF based on user input"""

        # Create PDF

        pdf = FPDF()

        pdf.add_page()

        

        # Set font

        pdf.set_font("Arial", "B", 16)

        

        # Header

        pdf.cell(0, 10, f"{document_type.upper()}: {name}", 0, 1, "C")

        pdf.set_font("Arial", "", 12)

        pdf.cell(0, 10, f"Email: {email}", 0, 1, "C")

        pdf.ln(5)

        

        # About section

        enhanced_about = self.enhance_with_ai(about, document_type)

        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "About", 0, 1)

        pdf.set_font("Arial", "", 12)

        pdf.multi_cell(0, 10, enhanced_about)

        pdf.ln(5)

        

        # Experience section

        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "Experience", 0, 1)

        for exp in experience:

            pdf.set_font("Arial", "B", 12)

            pdf.cell(0, 10, f"{exp['title']} at {exp['company']}", 0, 1)

            pdf.set_font("Arial", "", 10)

            pdf.cell(0, 10, f"{exp['startDate']} - {exp['endDate']}", 0, 1)

            enhanced_desc = self.enhance_with_ai(exp['description'], document_type)

            pdf.multi_cell(0, 10, enhanced_desc)

            pdf.ln(5)

        

        # Education section

        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "Education", 0, 1)

        for edu in education:

            pdf.set_font("Arial", "B", 12)

            pdf.cell(0, 10, f"{edu['degree']} from {edu['institution']}", 0, 1)

            pdf.set_font("Arial", "", 10)

            pdf.cell(0, 10, f"{edu['startDate']} - {edu['endDate']}", 0, 1)

            pdf.ln(5)

        

        # Skills section

        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "Skills", 0, 1)

        pdf.set_font("Arial", "", 12)

        skill_text = ", ".join([skill['name'] for skill in skills])

        pdf.multi_cell(0, 10, skill_text)

        

        # Save PDF to temporary file

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        pdf_path = temp_file.name

        temp_file.close()

        pdf.output(pdf_path)

        

        return pdf_path