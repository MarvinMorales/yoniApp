from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import mysql.connector
from os import getenv
from emailSender import EmailSender
from dotenv import load_dotenv
import json
import jwt

app = Flask(__name__)
CORS(app)

app.config['__port'] = 12000
app.config['__host'] = '127.0.0.1'
app.config['__secret_JWT'] = '__|api_Hass_Marv|__'

#___ Connection to DataBase ___#
def connectDataBase() -> mysql.connector:
    conn = mysql.connector.connect(
        host="7aamin.mysql.pythonanywhere-services.com",
        database="7aamin$yonidb",
        user="7aamin",
        passwd="Hassi2016!")
    return conn

#_____  External methods and functions of server  _____#
def Encode_jwt(__payload:str) -> str:
  token_bytes = jwt.encode(__payload, key=app.config['__secret_JWT'], algorithm='HS512')
  return token_bytes

def Validate_token(__token:str) -> str:
  try:
    jwt.decode(__token, key=app.config['__secret_JWT'], algorithms=['HS256', 'HS512'])
    return "Valid"
  except jwt.exceptions.DecodeError:
    return "__TOKEN NOT VALID__"
  except jwt.ExpiredSignatureError:
    return "__TOKEN EXPIRED__"
  except jwt.InvalidTokenError:
    return "__TOKEN NOT VALID__"

@app.before_first_request
def middleware() -> load_dotenv:
    load_dotenv()

@app.after_request
def add_header(response:str) -> str:
    response.cache_control.max_age = 300
    return response

#___ Initial Route to the server ___#
@app.route("/", methods=["GET"])
@cross_origin()
def index_route() -> render_template:
    return render_template("index.html", title="Welcome!"), 200

#___ Initial Route to the server ___#
@app.route("/get/token", methods=["GET"])
@cross_origin()
def token_generator() -> dict:
    token = Encode_jwt({"user": f"__USER__{datetime.now()}", 'exp': datetime.now() + timedelta(days=1)})
    return {"success": True, "token": token}

#___ Route to get comments from server ___#
@app.route("/get_comments/<token>", methods=["GET"])
@cross_origin()
def get_comments(token:str) -> dict:
    if validation := Validate_token(token) == "Valid":
        if conn := connectDataBase():
            cursor = conn.cursor()
            cursor.execute("Select * from `commentstable`")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return {"success": True, "data": [list(x) for x in result]}, 200
    else: return {"success": False, "reason": validation}, 401

@app.route("/get_clients/<string:token>", methods=["GET"])
@cross_origin()
def get_clients(token:str) -> dict:
    if validation := Validate_token(token) == "Valid":
        if conn := connectDataBase():
            cursor = conn.cursor()
            cursor.execute("Select * from `clientstable`")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return {"success": True, "data": [list(x) for x in result]}, 200
    else: return {"success": False, "reason": validation}, 401

#___ Route to set clients info to DB ___#
@app.route("/save/client_info", methods=["POST"])
@cross_origin()
def save_clients_info() -> dict:
    if request.method == "POST":
        requestt = json.loads(request.data)
        if validation := Validate_token(requestt['token']) == "Valid":
            if conn := connectDataBase():
                cursor = conn.cursor()
                cursor.execute(f"""Insert into `clientstable`
                (`name`, `lastname`, `email`, `phone`) values
                ('{requestt['name']}', '{requestt['lastname']}', '{requestt['email']}', '{requestt['phone']}')""")
                conn.commit()
                cursor.close()
                conn.close()
                return {"success": True, "data": "Data saved in DB"}, 200
        else: return {"success": False, "reason": "__Forbidden__", "validaion": validation}, 401


#___ Route to set comments to DB ___#
@app.route("/save/client_comments", methods=["POST"])
@cross_origin()
def save_clients_comments() -> dict:
    if request.method == "POST":
        requestt = json.loads(request.data)
        if validation := Validate_token(requestt['token']) == "Valid":
            if conn := connectDataBase():
                cursor = conn.cursor()
                cursor.execute(f"""Insert into `commentstable`
                (`name`, `lastname`, `comment`) values
                ('{requestt['name']}', '{requestt['lastname']}', '{requestt['comment']}')""")
                conn.commit()
                cursor.close()
                conn.close()
                return {"success": True, "data": "Comment saved in DB"}, 200
        else: return {"success": False, "reason": "__Forbidden__", "validaion": validation}, 401


#___ Route to set comments to DB ___#
@app.route("/saravana/emailSender/<_token>/<_from>/<_to>/<_time>", methods=["GET"])
@cross_origin()
def saravana_email_sender(_token:str, _from:str, _to:str, _time:str) -> dict:
    if request.method == "GET":
        if validation := Validate_token(_token) == "Valid":
            sender = EmailSender(_from, _to, _time)
            return sender.sendEmail()
        else: return {"success": False, "reason": "__Forbidden__", "validaion": validation}, 401

if __name__ == "__main__":
  app.run(debug=True, host=app.config['__host'], port=app.config['__port'])
