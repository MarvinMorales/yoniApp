#_____  External methods and functions of server  _____#
import jwt

def Encode_jwt(__payload:str) -> str:
  token_bytes = jwt.encode(__payload, key='__|api_Hass_Marv|__', algorithm='HS512')
  return token_bytes

def Validate_token(__token:str) -> str:
  try:
    jwt.decode(__token, key='__|api_Hass_Marv|__', algorithms=['HS256', 'HS512'])
    return {"response": "Valid"}
  except jwt.exceptions.DecodeError as err:
    return {"response": "__TOKEN NOT VALID__", "err": str(err)}
  except jwt.ExpiredSignatureError as err:
    return {"response": "__TOKEN EXPIRED__", "err": str(err)}
  except jwt.InvalidTokenError as err:
    return {"response": "__TOKEN NOT VALID__", "err": str(err)}