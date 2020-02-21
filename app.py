from flask import Flask
from modules.utils import get_config

config = get_config()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
