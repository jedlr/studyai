from flask import Flask, request, render_template, jsonify, send_file
import openai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import bleach

app = Flask(__name__)

# Set your OpenAI API key 
# Carlos API
openai.api_key = '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'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = file.filename
        file_content = file.read()

        # Generate a summary, comprehension questions, and solutions using OpenAI
        summary = generate_summary(file_content)
        questions = generate_q(file_content)
        solutions = generate_sol(questions, file_content)
        citations = generate_citation(solutions, file_content)

        return jsonify({'result': summary, 'questions': questions, 'solutions': solutions, 'citations': citations})

@app.route('/new-comprehension-question', methods=['GET'])
def new_comprehension_question():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part for new question'})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file for new question'})

    if file:
        file_content = file.read()

        # Generate a new comprehension question using OpenAI
        new_question = generate_q(file_content)

        return jsonify({'newQuestion': new_question[0]})

def generate_summary(text):
    # Decode the file content from bytes to a string
    text = text.decode('utf-8')
    
    # Use the OpenAI API to generate a summary
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Generate detailed summary for the following text'{text}' in bullet point format",
        max_tokens=700,  # Adjust the token limit as needed
        n=1,
    )
    result_summary = response.choices[0].text.strip()
    return result_summary


def generate_q(text):
    # Use the OpenAI API to generate comprehension questions
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Generate one comprehension question for the following text:\n{text}",
        max_tokens=200,  # Adjust the token limit as needed
        n=1,  # Number of questions to generate
    )

    questions = [choice.text for choice in response.choices]
    
    return questions

def generate_sol(questions, text):
    # Generate solutions for the comprehension questions using OpenAI
    solutions = []
    for question in questions:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Answer the following question based on the text:\n{question}\n\n{text}",
            max_tokens=200,  # Adjust the token limit as needed
            n=1,
        )
        solutions.append(response.choices[0].text)
    
    return solutions

def generate_citation(solutions, file_content):
    # Decode the file content from bytes to a string
    text = file_content.decode('utf-8')
    
    # Generate citations for the solutions by searching for solution keywords in the text
    citations = []

    for solution in solutions:
        # Use a simple text search to find the sentence containing the solution keyword
        solution_sentence = find_sentence_with_keyword(text, solution)
        
        if solution_sentence:
            citations.append(solution_sentence)
        else:
            citations.append("Citation not found for this solution")
    
    return citations


def find_sentence_with_keyword(text, keyword):
    # Split the text into sentences
    sentences = text.split('.')
    
    # Find the sentence containing the keyword
    for sentence in sentences:
        if keyword in sentence:
            return sentence.strip() + '.'
    
    return None

""" TODO: GENERATE PDF 
@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    content = request.form.get('content')
    questions = request.form.get('questions')
    solutions = request.form.get('solutions')
    
    if content is not None:
        # Sanitize the content, questions, and solutions using bleach
        content = bleach.clean(content)
        questions = bleach.clean(questions)
        solutions = bleach.clean(solutions)
    
        # Create a PDF buffer
        buffer = BytesIO()
    
        # Create a PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Add content, questions, and solutions to the PDF
        elements.append(Paragraph("Summary:", styles['Heading1']))
        elements.append(Paragraph(content, styles['Normal']))
        elements.append(Paragraph("Comprehension Questions:", styles['Heading1']))
        elements.append(Paragraph(questions, styles['Normal']))
        elements.append(Paragraph("Solutions:", styles['Heading1']))
        elements.append(Paragraph(solutions, styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name='summary.pdf', mimetype='application/pdf')
    else:
        # Handle the case when 'content' is None and return an error response
        return jsonify({'error': 'No content to generate PDF'})

"""

if __name__ == '__main__':
    app.run(debug=True)
