from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import mysql.connector
from os import getenv
from modules.emailSender import EmailSender
from modules.tokenization import Encode_jwt, Validate_token
from dotenv import load_dotenv
import asyncio
import jwt

saravana = Blueprint('saravana', __name__, url_prefix = "/saravana")
CORS(saravana)

#___ Connection to DataBase ___#
def connectDataBase() -> mysql.connector:
    conn = mysql.connector.connect(
        host="7aamin.mysql.pythonanywhere-services.com",
        database="7aamin$saravanadb",
        user="7aamin",
        passwd="Hassi2016!")
    return conn

@saravana.before_app_first_request
def middleware() -> load_dotenv:
    load_dotenv()

@saravana.after_request
def add_header(response:str) -> str:
    response.cache_control.max_age = 300
    return response

async def awaiting_for_emails_sent(_from, _to, _time) -> dict:
    sender = EmailSender(_from, _to, _time)
    response = await sender.sendEmail()
    return dict(response)

#___ Initial Route to the server ___#
@saravana.route("/get/token", methods=["GET"])
@cross_origin()
def token_generator() -> dict:
    token = Encode_jwt({"user": f"__USER__{datetime.now()}", 'exp': datetime.now() + timedelta(days=1)})
    return {"success": True, "token": token}

#___ Route to set comments to DB ___#
@saravana.route("/saravana/emailSender/<_token>/<_from>/<_to>/<_time>", methods=["GET"])
@cross_origin()
def saravana_email_sender(_token:str, _from:str, _to:str, _time:str) -> dict:
    if request.method == "GET":
        validation = Validate_token(_token)
        if validation['response'] == "Valid":
            asyncio.run(awaiting_for_emails_sent(_from, _to, _time))
        else: return {"success": False, "reason": "__Forbidden__", "validaion": validation['err']}, 401