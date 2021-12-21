from os import getenv
from dotenv import load_dotenv
from flask import Flask
from apis.yoni import yoni
from apis.saravana import saravana

app = Flask(__name__)
app.config['__port'] = 12000
app.config['__host'] = '127.0.0.1'

@app.before_first_request
def middleware(): load_dotenv()

if __name__ == "__main__":
    app.register_blueprint(yoni)
    app.register_blueprint(saravana)
    app.run(debug=True, host=app.config['__host'], port=app.config['__port'])
