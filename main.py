from .api import bp as api
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')


@app.get('/ping')
def ping_pong():
    return 'Pong!'
