from flask import Flask

app = Flask(__name__)


@app.get('/ping')
def ping_pong():
    return 'Pong!'
