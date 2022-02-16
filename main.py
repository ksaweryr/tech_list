from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)


@app.get('/ping')
def ping_pong():
    return 'Pong!'
