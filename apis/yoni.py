from flask import Blueprint, render_template, request
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import mysql.connector
from os import getenv
from modules.emailSender import EmailSender
from modules.tokenization import Encode_jwt, Validate_token
from dotenv import load_dotenv
import json

yoni = Blueprint('yoni', __name__, url_prefix = "/yoni")
CORS(yoni)

#___ Connection to DataBase ___#
def connectDataBase() -> mysql.connector:
    conn = mysql.connector.connect(
        host="7aamin.mysql.pythonanywhere-services.com",
        database="7aamin$yonidb",
        user="7aamin",
        passwd="Hassi2016!")
    return conn

@yoni.before_app_first_request
def middleware() -> load_dotenv:
    load_dotenv()

@yoni.after_request
def add_header(response:str) -> str:
    response.cache_control.max_age = 300
    return response

#___ Initial Route to the server ___#
@yoni.route("/", methods=["GET"])
@cross_origin()
def index_route() -> render_template:
    return render_template("index.html", title="Welcome!"), 200

#___ Initial Route to the server ___#
@yoni.route("/get/token", methods=["GET"])
@cross_origin()
def token_generator() -> dict:
    token = Encode_jwt({"user": f"__USER__{datetime.now()}", 'exp': datetime.now() + timedelta(days=1)})
    return {"success": True, "token": token}

#___ Route to get comments from server ___#
@yoni.route("/get_comments/<token>", methods=["GET"])
@cross_origin()
def get_comments(token:str) -> dict:
    validation = Validate_token(token)
    if validation['response'] == "Valid":
        if conn := connectDataBase():
            cursor = conn.cursor()
            cursor.execute("Select * from `commentstable`")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return {"success": True, "data": [list(x) for x in result]}, 200
    else: return {"success": False, "reason": validation['err']}, 401

@yoni.route("/get_clients/<string:token>", methods=["GET"])
@cross_origin()
def get_clients(token:str) -> dict:
    validation = Validate_token(token)
    if validation['response'] == "Valid":
        if conn := connectDataBase():
            cursor = conn.cursor()
            cursor.execute("Select * from `clientstable`")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return {"success": True, "data": [list(x) for x in result]}, 200
    else: return {"success": False, "reason": validation['err']}, 401

#___ Route to set clients info to DB ___#
@yoni.route("/save/client_info", methods=["POST"])
@cross_origin()
def save_clients_info() -> dict:
    if request.method == "POST":
        requestt = json.loads(request.data)
        validation = Validate_token(requestt['token'])
        if validation['response'] == "Valid":
            if conn := connectDataBase():
                cursor = conn.cursor()
                cursor.execute(f"""Insert into `clientstable`
                (`name`, `lastname`, `email`, `phone`) values
                ('{requestt['name']}', '{requestt['lastname']}', '{requestt['email']}', '{requestt['phone']}')""")
                conn.commit()
                cursor.close()
                conn.close()
                return {"success": True, "data": "Data saved in DB"}, 200
        else: return {"success": False, "reason": "__Forbidden__", "validaion": validation['err']}, 401


#___ Route to set comments to DB ___#
@yoni.route("/save/client_comments", methods=["POST"])
@cross_origin()
def save_clients_comments() -> dict:
    if request.method == "POST":
        requestt = json.loads(request.data)
        validation = Validate_token(requestt['token'])
        if validation['response'] == "Valid":
            if conn := connectDataBase():
                cursor = conn.cursor()
                cursor.execute(f"""Insert into `commentstable`
                (`name`, `lastname`, `comment`) values
                ('{requestt['name']}', '{requestt['lastname']}', '{requestt['comment']}')""")
                conn.commit()
                cursor.close()
                conn.close()
                return {"success": True, "data": "Comment saved in DB"}, 200
        else: return {"success": False, "reason": "__Forbidden__", "validaion": validation['err']}, 401
