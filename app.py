from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, ServiceContext
# , GPTListIndex, readers
from langchain import OpenAI
# from pathlib import Path
from dotenv import load_dotenv
import os
import urllib.request
import datetime

# import sys
# import tkinter
# from tkinter import ttk, messagebox
# from IPython.display import Markdown, display
# from datetime import timedelta

from flask import Flask, render_template, request, redirect, url_for, session
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
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "somethingsunique"
# session.init_app(app)


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


@app.route('/logout/', methods=['POST'])
def logout():
    session["name"] = None
    return redirect(url_for('index'))


@app.route('/connect/', methods=['POST'])
def connect():
    otp_publickey = request.form.get('otp_publickey')
    ESSU_id = request.form.get('ESSU_id').upper().strip()
    password = request.form.get('Password')

    essu_login = True
    motp_gencode = 0
    auditstr = ""
    essusucc_login = False

    i = 0
    for i in range(0, len(ESSU_id)):
        gencode_val = ord(ESSU_id[i:i+1]) * (i + 1)
        motp_gencode = motp_gencode + gencode_val
        i = i + 1

    motp_gencode = motp_gencode * int(password) * int(otp_publickey)
    sotp_gencode = str(motp_gencode).strip()
    sysgencode = otp_gencode(sotp_gencode[:6], 6)

    User_ID = request.form.get('User_ID').strip()
    if sysgencode == User_ID.ljust(6, "9"):
        essusucc_login = True
    else:
        essusucc_login = False

    link = "http://support.epointsg.com/download/TOKEN/" + ESSU_id.upper().strip() + ".txt"
    print(link)
    webtoken = urllib.request.urlopen(link).read().decode('utf-8')
    urllib.request.urlopen(link).close()

    if webtoken == False:
        webtoken = ""

    rgencode = 0
    succ_login = False

    nowdt = datetime.datetime.now().strftime(f"%Y%m%d%H%M")
    scurrentstring = ESSU_id.upper() + nowdt

    rgencode = get_webtoken(scurrentstring, password)
    print(webtoken)
    print(rgencode)
    if webtoken == rgencode:
        essusucc_login = True
    else:
        minutes_before = (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime(f"%Y%m%d%H%M")
        scurrentstring = ESSU_id.upper() + minutes_before
        rgencode = get_webtoken(scurrentstring, password)
        if webtoken == rgencode:
            essusucc_login = True
        else:
            minutes_after = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime(f"%Y%m%d%H%M")
            scurrentstring = ESSU_id.upper() + minutes_after
            rgencode = get_webtoken(scurrentstring, password)
            if webtoken == rgencode:
                essusucc_login = True
            else:
                print(essusucc_login)
                errmsg = 'Login failed! Try again.[' + rgencode + '/' + webtoken + ']'
                return redirect(url_for('index', errmsg=errmsg))

    if essusucc_login == True:
        print(essusucc_login)
        session["name"] = request.form.get(request.form.get('User_ID'))
        return redirect(url_for('index'))



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
            openaiquestion = question.strip()

    epointData = EpointData(question, answer, department)
    db.session.add(epointData)
    db.session.commit()
    epoint_datas = EpointData.query.filter_by(department='Admin').all()

    #    flask("Book added successful")

    if request.form.get('isAdmin') == 'Admin':
        return redirect(url_for('indexadmin'))
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


def otp_gencode(msource, mcodelen):
    codestr = "1234567890012345678978901234562345678901567890123478901234568901234567789012345601234567896789012345123456789089012345673" \
              "456789012678901234567890123457890123456678901234556789012347890123456789012345678901234561234567890012345678945678901232345678901" \
              "789012345656789012341234567890012345678945678901237890123456123456789056789012344567890123456789012312345678900123456789234567890" \
              "156789012344567890123012345678990123456781234567890789012345656789012347890123456456789012312345678900123456789345678901212345678" \
              "901234567890789012345690123456781234567890901234567890123456783456789012234567890190123456781234567890345678901290123456781234567" \
              "890789012345623456789016789012345678901234556789012343456789012123456789045678901230123456789123456789012345678902345678901234567" \
              "890156789012343456789012123456789067890123453456789012456789012389012345678901234567345678901245678901232345678901567890123412345" \
              "678907890123456901234567878901234569012345678123456789034567890128901234567567890123423456789012345678901"

    tgencode = ""
    straudit = ""
    len_source = len(msource) - 1

    x = 0
    for x in range(0, len_source):
        tcodestrno = (int(msource[x:x+2]) * 10) + (x + 1)
        tgencode = tgencode + codestr[tcodestrno - 1:1]
        straudit = straudit + str(x) + "->" + str(tcodestrno) + '/' + tgencode + "     "
        x = x + 1

    return tgencode[-1 *mcodelen:]


def get_webtoken(msource, password):
    rgencode = 0
    loopcnt = 0
    len_source = len(msource)

    i = 0
    for i in range(0, len_source):
        loopcnt += 1
        rgencode = rgencode + ord(msource[i:i+1]) * (i + 1)
        i += 1

    rgencode = str(rgencode * int(password))
    rgencode = rgencode.strip()

    return rgencode

if __name__ == "__main__":
    app.run(debug=True)
