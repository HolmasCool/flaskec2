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

import tkinter
from tkinter import ttk, messagebox

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
# app.config['SQLALCHEMY_BINDS'] = {
#     'auth': 'mysql://epointadmin:200200170hH@epointaichat.cb1yssr93nnk.ap-southeast-1.rds' \
#             '.amazonaws.com/EpointContext'}
#
# app.config["SQLALCHEMY_ECHO"] = True
# app.config["SQLALCHEMY_RECORD_QUERIES"] = True

db = SQLAlchemy(app)


class epoint_data(db.Model):
    # __bind_key__ = "auth"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(LONGTEXT, nullable=False)
    answer = db.Column(LONGTEXT, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.TIMESTAMP(), nullable=False)

    def __init__(self, question, answer, department):
        self.question = question
        self.answer = answer
        self.department = department


# flask shell
# a = epoint_data(question='What is postcode of Epoint Sytems Pte Ltd?', answer='609964', department='Admin')
# b = epoint_data(question='What is unt number of Epoint Systems?', answer='#02-09', department='Admin')
# c = epoint_data(question='Where is Epoint Sytems Pte Ltd?', answer='Trade Hub 21, 8 Boon Lay Way', department='Admin')
# db.session.add(c)
# db.sesssion.commit()

@app.route('/')
def index():
    epoint_datas = epoint_data.query.all()
    return render_template('index.html', epoint_datas=epoint_datas)
    # render_template('index.html')


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
        tkinter.messagebox.showwarning("EPoint AI Chat bot Answer", message=response.response)
        break


# def print_hi():
#     # # Use a breakpoint in the code line below to debug your script.
#     # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# if __name__ == '__main__':

# Press the green button in the gutter to run the script.q
if __name__ == '__main__':
    app.run(debug=True)
    # ask_ai()
    window = tkinter.Tk()
    window.title("Epoint Systems Support AI Chat bot")

    frame = tkinter.Frame(window)
    frame.pack()

    # Saving User Info
    user_info_frame = tkinter.LabelFrame(frame, text="User Information")
    user_info_frame.grid(row=0, column=0, padx=200, pady=10)

    first_name_label = tkinter.Label(user_info_frame, text="First Name")
    first_name_label.grid(row=0, column=0)

    last_name_label = tkinter.Label(user_info_frame, text="Last Name")
    last_name_label.grid(row=0, column=1)

    openai_secret_key = tkinter.Label(user_info_frame, text="OpenAI Secret Key")
    openai_secret_key.grid(row=0, column=2)

    first_name_entry = tkinter.Entry(user_info_frame)
    last_name_entry = tkinter.Entry(user_info_frame)
    openai_secret_key_entry = tkinter.Entry(user_info_frame)
    first_name_entry.grid(row=1, column=0)
    last_name_entry.grid(row=1, column=1)

    openai_secret_key_entry.grid(row=1, column=2)

    AI_Chat_bot_frame = tkinter.LabelFrame(frame, text="AI Chat bot")
    AI_Chat_bot_frame.grid(row=1, column=0, sticky="news", padx=200, pady=10)

    Question_label = tkinter.Label(AI_Chat_bot_frame, text="Question to ask?")
    Question_entry = tkinter.Entry(AI_Chat_bot_frame)
    Question_label.grid(row=0, column=0)
    Question_entry.grid(row=0, column=1)

    for widget in user_info_frame.winfo_children():
        widget.grid_configure(padx=10, pady=5)

    for widget in AI_Chat_bot_frame.winfo_children():
        widget.grid_configure(padx=10, pady=5)

    # Button
    button = tkinter.Button(frame, text="Enter", command=ask_ai)
    button.grid(row=3, column=0, sticky="news", padx=200, pady=10)

    window.mainloop()
