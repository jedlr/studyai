from flask import Flask, request, render_template, jsonify
from sentence_transformers import SentenceTransformer
import openai

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

    # Split the summary into bullet points
    bullet_points = [point.strip('-', ':') for point in result_summary.split('\n')]

    return bullet_points



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


def find_sentence_with_keyword(text, keywords):
    # Split the text into sentences
    #print(text)
    #print(keywords)
    sentences = text.split('.')
    keyword = keywords.split()

    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings = model.encode(sentences)
    print(embeddings)

    sentence_to_embedding = dict(zip(sentences, embeddings))

    # To print out the text corresponding to an embedding
    target_embedding = embeddings[2]  # Replace with the index of the embedding you want to retrieve
    text = next(key for key, value in sentence_to_embedding.items() if (value == target_embedding).all())
    print(text)

    """"
    # Find the sentence containing the keyword
    for sentence in sentences:
        for keyword in keywords:
            if keyword in sentence:
                #print("Keyword Found")
                return sentence.strip() + '.'
    """
    #print("Keyword Not Found")
    return text



if __name__ == '__main__':
    app.run(debug=True)
