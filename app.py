from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, ServiceContext
# , GPTListIndex, readers
from langchain import OpenAI
# from pathlib import Path
from dotenv import load_dotenv
import os
# import sys
# import tkinter
# from tkinter import ttk, messagebox
# from IPython.display import Markdown, display
# from datetime import timedelta

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

# env_path = Path('.', '.env')
# load_dotenv(dotenv_path='\vevn\.env')
load_dotenv()

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://' + os.getenv('SQLUSERNAME') + ':' + os.getenv('SQLPASSWORD') + '@' \
                                 + os.getenv('SQLSERVER') + '.cb1yssr93nnk.ap-southeast-1.rds' \
                                                            '.amazonaws.com/EpointContext'

app.config['SQLACHEMY_TRACK_MODIFICATION'] = os.getenv("SQLACHEMY_TRACK_MODIFICATION")
db = SQLAlchemy(app)


# app.secret_key = "somethingsunique"

class EpointData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    question = db.Column(LONGTEXT, nullable=False)
    answer = db.Column(LONGTEXT, nullable=False)
    if answer is None:
        answer = ''
    if department is None:
        department = 'Question'

    def __init__(self, question='', answer='', department=''):
        self.question = question
        self.answer = answer
        self.department = department


@app.route('/')
def index():
    openaianswer = request.args.get('openaianswer')
    openaiquestion = request.args.get('openaiquestion')
    if openaianswer is None:
        openaianswer = ''
    if openaiquestion is None:
        openaiquestion = ''
    epoint_datas = EpointData.query.filter(EpointData.department != 'Question').all()
    return render_template('index.html', openaianswer=openaianswer, openaiquestion=openaiquestion, epoint_datas=epoint_datas)


@app.route('/indexadmin/', methods=['GET'])
def indexadmin():
    epoint_datas = EpointData.query.all()
    return render_template('indexadmin.html', epoint_datas=epoint_datas, indicator='Admin')


@app.route('/Delete/', methods=['GET'])
def delete_epointdata_indexadmin():
    db.session.delete(EpointData.query.get(request.args.get('id')))
    db.session.commit()
    return redirect(url_for('indexadmin'))

@app.route('/Update/', methods=['GET'])
def update_context_data():
    file_to_use = open('context_data/data/epoint_data.txt', 'w+')
    epoint_datas = EpointData.query.filter(EpointData.department != 'Question').all()

    for epoint_data in epoint_datas :
        file_to_use.write('Interviewer:'+epoint_data.question.strip() + '\n')
        file_to_use.write('Interviewee:' +epoint_data.answer.strip() + '\n')
    file_to_use.close()

    return redirect(url_for('indexadmin'))



@app.route('/add/', methods=['POST'])
def insert_question():
    openaianswer = ''
    openaiquestion = ''
    department = ''
    question = ''
    answer = ''

    if request.method == "POST":
        department = request.form.get('txtDepartment')
        question = request.form.get('question')
        answer = request.form.get('answer')
        if answer is None:
            answer = ''

        if department is None:
            department = 'Question'
            answer = ''

        if answer == '' and department == 'Question':
            openaianswer = ask_ai(question)
            openaiquestion = question

    epointData = EpointData(question, answer, department)
    db.session.add(epointData)
    db.session.commit()
    epoint_datas = EpointData.query.filter_by(department='Admin').all()

    #    flask("Book added successful")

    if request.form.get('isAdmin') == 'Admin':
        return redirect(url_for('indexadmin', epoint_datas=epoint_datas))
    else:
        return redirect(
            url_for('index', openaianswer=openaianswer, openaiquestion=openaiquestion, epoint_datas=epoint_datas))

    # return render_template('index.html', openaianswer=openaianswer, openaiquestion=openaiquestion,
    #                        epoint_datas=epoint_datas)


def construct_index(directory_path):
    # set maximum input size
    max_input_size = 4096
    # set number of output tokens
    num_outputs = 2000
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 600

    # define prompt helper
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    # define LLM
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003", max_tokens=num_outputs))

    documents = SimpleDirectoryReader(directory_path).load_data()

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    GPTindex = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
    GPTindex.save_to_disk('index.json')
    return GPTindex


def ask_ai(question):
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    construct_index("context_data/data")
    GPTindex = GPTSimpleVectorIndex.load_from_disk('index.json')
    response = GPTindex.query(question)
    return response


if __name__ == "__main__":
    app.run(debug=True)
