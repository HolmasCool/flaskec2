from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper,\
    ServiceContext
from langchain import OpenAI
import os
# import sys
# import tkinter
# from tkinter import ttk, messagebox
# from IPython.display import Markdown, display

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://epointadmin:200200170hH@epointaichat.cb1yssr93nnk.ap-southeast-1.rds' \
                                 '.amazonaws.com/EpointContext'
app.config['SQLACHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)


class EpointData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(LONGTEXT, nullable=False)
    answer = db.Column(LONGTEXT, nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def __init__(self, question, answer, department):
        self.question = question
        self.answer = answer
        self.department = department


@app.route('/')
def index():
    epoint_datas = EpointData.query.all()
    return render_template('index.html', epoint_datas=epoint_datas)


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
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)

    index.save_to_disk('index.json')

    return index


def ask_ai():
    secret_key = openai_secret_key_entry.get()
    os.environ["OPENAI_API_KEY"] = secret_key
    os.environ["OPENAI_API_KEY"] = "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"
    construct_index("context_data/data")

    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    query = Question_entry.get()

    while True:
        # query = input("What do you want to ask? ")
        response = index.query(query)
        # display(Markdown(f"Response: <b>{response.response}</b>"))
        # print(response.response)
        # tkinter.messagebox.showwarning("EPoint AI Chat bot Answer", message=response.response)
        break


if __name__ == "__main__":
    app.run(debug=True)