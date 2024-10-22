from flask import Flask, request, render_template, jsonify, session
from openai import OpenAI

client = OpenAI(api_key='your_api_key_here')
# from transformers import AutoTokenizer, AutoModel
# import torch
# import torch.nn.functional as F
# from sentence_transformers import SentenceTransformer

app = Flask(__name__)
app.secret_key = 'cool'

# Set your OpenAI API key
# Carlos API
#openai.api_key = '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'
#Johana API


# # Load the Sentence Transformers model
# sentence_transformer_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# # Load the Hugging Face model and tokenizer
# hf_model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')
# hf_tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')

# # Mean Pooling - Take attention mask into account for correct averaging
# def mean_pooling(model_output, attention_mask):
#     token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
#     input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
#     return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

@app.route('/')
def index():
    return render_template('index.html', active_page='index')

@app.route('/upload')
def upload():
    return render_template('upload.html', active_page='upload')

@app.route('/submit_question', methods=['POST'])
def submit_question():
    question = request.form.get('question')
    if not question:
        return jsonify({'error': 'No question provided'})

    # Assuming you have the text content available. 
    # You might need to adjust this based on your application's logic.
    text_content = get_text_content()  # Implement this function as per your application's logic

    answer = generate_answer(question, text_content)
    return jsonify({'answer': answer})

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
        numbered_questions = [f"{idx + 1}. {question}" for idx, question in enumerate(questions)]
        numbered_solutions = [f"{idx + 1}. {solution}" for idx, solution in enumerate(solutions)]

        return jsonify({'result': summary, 'questions': numbered_questions, 'solutions': numbered_solutions, 'citations': citations})

def generate_summary(text):
    # Decode the file content from bytes to a string
    text = text.decode('utf-8')
    print("text:", text)
    # Use the OpenAI API to generate a summary
    response = client.completions.create(model="text-davinci-003",
    prompt=f"Generate detailed summary for the following text'{text}' using dashes format",
    max_tokens=700,  # Adjust the token limit as needed
    n=1)
    result_summary = response.choices[0].text.strip()
    print(result_summary)
    # Split the summary into bullet points
    bullet_points = [point.strip('-') for point in result_summary.split('\n')]

    session['generated_summary'] = bullet_points

    return bullet_points

def generate_q(text):
    # Use the OpenAI API to generate comprehension questions
    response = client.completions.create(model="text-davinci-003",
    prompt=f"Generate one comprehension question for the following text:\n{text}",
    max_tokens=200,  # Adjust the token limit as needed
    n=1)

    questions = [choice.text for choice in response.choices]

    return questions

def generate_sol(questions, text):
    # Generate solutions for the comprehension questions using OpenAI
    solutions = []
    for question in questions:
        response = client.completions.create(model="text-davinci-003",
        prompt=f"Answer the following question based on the text:\n{question}\n\n{text}",
        max_tokens=200,  # Adjust the token limit as needed
        n=1)
        solutions.append(response.choices[0].text)

    return solutions

def generate_citation(solutions, text):
    citations = []
    for solution in solutions:
        prompt = f"Extract a citation for the following answer in the context of the provided text:\nAnswer: {solution}\nText: {text}"
        response = client.completions.create(model="text-davinci-003",  # Updated model version
                                             prompt=prompt,
                                             max_tokens=150,  # Adjust as needed
                                             n=1)
        citation = response.choices[0].text.strip()
        citations.append(citation)

    print("citations:", citation)
    return citations

def generate_answer(question, text):
    response = client.completions.create(
        model="text-davinci-003",
        prompt=f"Answer this question based on the following text:\nQuestion: {question}\nText: {text}",
        max_tokens=200  # Adjust the token limit as needed
    )
    answer = response.choices[0].text.strip()
    return answer

def get_text_content():
    # Retrieve the summary from the session
    return session.get('generated_summary', "No summary has been generated yet.")


if __name__ == '__main__':
    app.run(debug=True)
