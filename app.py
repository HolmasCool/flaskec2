from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, \
    ServiceContext
from langchain import OpenAI
import os
#import sys
# import tkinter
# from tkinter import ttk, messagebox


from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT


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
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)