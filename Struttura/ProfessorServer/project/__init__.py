from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # key encrypt cookie
    app.config['SECRET_KEY'] = "apl_prof_server"

    return app


