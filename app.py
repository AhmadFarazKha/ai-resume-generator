from flask import Flask, render_template, request, send_file, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json
import uuid
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/downloads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Google API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config
)

def create_resume_pdf(data, doc_type):
    """Creates a PDF resume/CV from the given data using ReportLab."""

    filename = f"{app.config['UPLOAD_FOLDER']}/{uuid.uuid4()}_{doc_type.lower().replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Personal Information Table
    personal_info = [
        ["Name:", data.get('name', 'User')],
        ["Email:", data.get('email', 'email@example.com')],
        ["LinkedIn:", data.get('linkedin', '')],
        ["GitHub:", data.get('github', '')],
    ]
    table = Table(personal_info)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)]))
    elements.append(table)

    # Experience Sections
    if 'sections' in data and 'Experience' in data['sections']:
        elements.append(Paragraph("<b>Experience</b>", styles['Heading1']))
        for item in data['sections']['Experience']:
            elements.append(Paragraph(f"<b>{item.get('title', '')}</b>", styles['Heading2']))
            elements.append(Paragraph(item.get('description', ''), styles['Normal']))

    # Education Sections
    if 'sections' in data and 'Education' in data['sections']:
        elements.append(Paragraph("<b>Education</b>", styles['Heading1']))
        for item in data['sections']['Education']:
            elements.append(Paragraph(f"<b>{item.get('title', '')}</b>", styles['Heading2']))
            elements.append(Paragraph(item.get('description', ''), styles['Normal']))

    # Image
    if 'image' in data:
        try:
            imgdata = base64.b64decode(data['image'].split(',')[1])
            img = Image(BytesIO(imgdata), width=100, height=100)
            elements.append(img)
        except Exception as e:
            print(f"Error handling image: {e}")

    doc.build(elements)
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_document():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        doc_type = request.form.get('doc_type')
        position = request.form.get('position')
        linkedin = request.form.get('linkedin')
        github = request.form.get('github')
        education = request.form.get('education')
        experience = request.form.get('experience')
        image = request.files.get('image')

        # Generate content using Gemini
        prompt = f"""
        Generate a professional {doc_type} for {name} with email {email}.
        Position applying for: {position}.
        LinkedIn: {linkedin}.
        GitHub: {github}.
        Education: {education}.
        Experience: {experience}.

        Structure the response as a JSON object with the following format:
        {{
            "name": "{name}",
            "email": "{email}",
            "sections": {{
                "Summary": "Professional summary goes here",
                "Experience": [
                    {{"title": "Job Title - Company (Year-Year)", "description": "Description of role and accomplishments"}},
                    // more experience items...
                ],
                "Education": [
                    {{"title": "Degree - Institution (Year)", "description": "Details about education"}},
                    // more education items...
                ],
                "Skills": ["Skill 1", "Skill 2", "Skill 3", ...],
                // other sections as needed...
            }}
        }}

        Make sure the result is strictly valid JSON with no extra text before or after.
        Include relevant professional sections that would be expected in a {doc_type}.
        Generate realistic and professional content that would be suitable for a job application.
        """

        response = model.generate_content(prompt)

        # Extract JSON from the response
        content = response.text
        # Remove any markdown code fences if present
        if content.startswith('```json'):
            content = content.split('```json')[1]
        if content.endswith('```'):
            content = content.rsplit('```', 1)[0]
            
        content = content.strip()

        # Parse the JSON content
        document_data = json.loads(content)

        # Handle Image
        image_base64 = None
        if image:
            try:
                image_base64 = 'data:image/jpeg;base64,' + base64.b64encode(image.read()).decode('utf-8')
            except Exception as e:
                print(f"Error encoding image: {e}")

        # Create PDF
        pdf_path = create_resume_pdf({**document_data, 'image': image_base64, 'linkedin': linkedin, 'github': github}, doc_type)

        # Return the path to the PDF file
        filename = os.path.basename(pdf_path)

        preview_data = {
            'name': name,
            'email': email,
            'sections': document_data.get('sections', {}),
            'image': image_base64,
            'linkedin': linkedin,
            'github': github,
        }

        return jsonify({
            'success': True,
            'message': f'{doc_type} generated successfully!',
            'filename': filename,
            'preview_data': preview_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating document: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(f"{app.config['UPLOAD_FOLDER']}/{filename}", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)