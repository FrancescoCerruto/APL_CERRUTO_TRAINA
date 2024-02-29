from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    # key encrypt cookie
    app.config['SECRET_KEY'] = os.urandom(12).hex()

    return app


