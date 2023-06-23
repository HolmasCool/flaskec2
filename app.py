# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/




from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

# import tkinter
# from tkinter import ttk, messagebox

from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, \
    ServiceContext
from langchain import OpenAI
import sys
import os
from IPython.display import Markdown, display

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://epointadmin:200200170hH@epointaichat.cb1yssr93nnk.ap-southeast-1.rds' \
                                 '.amazonaws.com/EpointContext'
app.config['SQLACHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

class epoint_data(db.Model):
    # __bind_key__ = "auth"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(LONGTEXT, nullable=False)
    answer = db.Column(LONGTEXT, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    # timestamp = db.Column(db.TIMESTAMP(), nullable=False)

    def __init__(self, question, answer, department):
        self.question = question
        self.answer = answer
        self.department = department

@app.route('/')

def index():
    return render_template('index2.html')
#zhiming
#    epoint_datas = epoint_data.query.all()
#    return render_template('index.html', epoint_datas=epoint_datas)



if __name__ == "__main__":
    app.run(debug=True)