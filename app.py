from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import mysql.connector
from os import getenv
from dotenv import load_dotenv
import json

app = Flask(__name__)
CORS(app)

app.config['__port'] = 12000
app.config['__host'] = '127.0.0.1'

#___ Connection to DataBase ___#
def connectDataBase() -> object:
    conn = mysql.connector.connect(
        host = getenv('DATA_BASE_HOST'),
        database = getenv('DATA_BASE'),
        user = getenv('DATA_BASE_USER'),
        password = getenv('DATA_BASE_PASS'))
    return conn

@app.before_first_request
def middleware() -> load_dotenv:
    load_dotenv()

@app.after_request
def add_header(response:str) -> str:
    response.cache_control.max_age = 300
    return response

"""#___ Initial Route to the server ___#
@app.route("/", methods=["GET"])
@cross_origin()
def index_route() -> render_template:
    return render_template("index.html", title="Welcome!"), 200"""

#___ Initial Route to the server ___#
@app.route("/", methods=["GET"])
@cross_origin()
def index_route() -> str:
    print(1222)
    return "Hola222"

#___ Route to get comments from server ___#
@app.route("/get_comments/<int:_from>/<int:_to>", methods=["GET"])
@cross_origin()
def get_comments(_from:int, _to:int) -> dict:
    with connectDataBase() as conn:
        cursor = conn.cursor()
        cursor.execute("Select (*) from `commentstable`")
        response = cursor.fetchall()[_from - 1:_to - 1]
        cursor.close()
        conn.close()
        print(response)
    return {"success": True, "data": response}, 200

@app.route("/get_clients", methods=["GET"])
@cross_origin()
def get_clients() -> dict:
    print(1222)
    with connectDataBase() as conn:
        cursor = conn.cursor()
        cursor.execute("Select * from `clientstable`")
        result = cursor.fetchall()
        print(result)
        return {"data": 200}, 200
    return "Nada"

#___ Route to set clients info to DB ___#
@app.route("/save/client_info", methods=["POST"])
@cross_origin()
def save_clients_info() -> dict:
    if request.method == "POST":
        name = request.json['name']
        lastname = request.json['lastname']
        email = request.json['email']
        phone = request.json['phone']
        with connectDataBase() as conn:
            cursor = conn.cursor()
            sql = """Insert into `clientstable`
            (`name`, `lastname`, `email`, `phone`) values
            ('%s', '%s', '%s', '%s')"""
            cursor.execute(sql, (name, lastname, email, phone))
            conn.commit()
            cursor.close()
            conn.close()
        return {"success": True, "data": "Data saved in DB"}, 200

#___ Route to set comments to DB ___#
@app.route("/save/client_comments", methods=["POST"])
@cross_origin()
def save_clients_comments() -> dict:
    if request.method == "POST":
        name = request.json['name']
        lastname = request.json['lastname']
        comment = request.json['comment']
        with connectDataBase() as conn:
            cursor = conn.cursor()
            sql = """Insert into `commentstable`
            (`name`, `lastname`, `comment`) values
            ('%s', '%s', '%s')"""
            cursor.execute(sql, (name, lastname, comment))
            conn.commit()
            cursor.close()
            conn.close()
        return {"success": True, "data": "Comment saved in DB"}, 200

if __name__ == "__main__":
  app.run(debug=False, host=app.config['__host'], port=app.config['__port'])
