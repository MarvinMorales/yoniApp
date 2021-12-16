from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import mysql.connector
from os import getenv
from dotenv import load_dotenv
import jwt

app = Flask(__name__)
CORS(app)

app.config['__port'] = 12000
app.config['__host'] = '127.0.0.1'

#___ Connection to DataBase ___#
def connectDataBase() -> object:
    conn = mysql.connector.connect(
        host="7aamin.mysql.pythonanywhere-services.com",
        database="7aamin$yonidb",
        user="7aamin",
        passwd="Hassi2016!")
    return conn

#_____  External methods and functions of server  _____#
def Encode_jwt(__payload:str) -> str:
  token_bytes = jwt.encode(__payload, getenv('SECRET'), algorithm = 'HS512')
  return token_bytes

def Validate_token(__token:str) -> str:
  try: 
    __result = jwt.decode(__token, getenv('SECRET'), algorithms = ['HS256', 'HS512'])
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
@app.route("/get_comments/<int:_from>/<int:_to>", methods=["GET"])
@cross_origin()
def get_comments(_from:int, _to:int) -> dict:
    if conn := connectDataBase():
        cursor = conn.cursor()
        cursor.execute("Select (*) from `commentstable`")
        response = cursor.fetchall()[_from - 1:_to - 1]
        cursor.close()
        conn.close()
        return {"success": True, "data": response}, 200

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
    else: return {"success": False, "reason": validation}

#___ Route to set clients info to DB ___#
@app.route("/save/client_info", methods=["POST"])
@cross_origin()
def save_clients_info() -> dict:
    if validation := Validate_token(request.json['token']) == "Valid":
        if request.method == "POST":
            name = request.json['name']
            lastname = request.json['lastname']
            email = request.json['email']
            phone = request.json['phone']
            if conn := connectDataBase():
                cursor = conn.cursor()
                sql = """Insert into `clientstable`
                (`name`, `lastname`, `email`, `phone`) values
                ('%s', '%s', '%s', '%s')"""
                cursor.execute(sql, (name, lastname, email, phone))
                conn.commit()
                cursor.close()
                conn.close()
                return {"success": True, "data": "Data saved in DB"}, 200
    else: return {"success": False, "reason": validation}


#___ Route to set comments to DB ___#
@app.route("/save/client_comments", methods=["POST"])
@cross_origin()
def save_clients_comments() -> dict:
    if validation := Validate_token(request.json['token']) == "Valid":
        if request.method == "POST":
            name = request.json['name']
            lastname = request.json['lastname']
            comment = request.json['comment']
            if conn := connectDataBase():
                cursor = conn.cursor()
                sql = """Insert into `commentstable`
                (`name`, `lastname`, `comment`) values
                ('%s', '%s', '%s')"""
                cursor.execute(sql, (name, lastname, comment))
                conn.commit()
                cursor.close()
                conn.close()
                return {"success": True, "data": "Comment saved in DB"}, 200
    else: return {"success": False, "reason": validation}


if __name__ == "__main__":
  app.run(debug=True, host=app.config['__host'], port=app.config['__port'])
