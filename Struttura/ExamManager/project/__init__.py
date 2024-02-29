from flask import Flask
from flask_mongoengine import MongoEngine
import os


# init SQLAlchemy so we can use it later in our models
db = MongoEngine()


# MONGO ENVIRONMENT
MONGODB_SETTINGS = {
    'db': os.getenv("MONGO_DB"),
    'host': os.getenv("MONGO_HOST")
}


def create_app():
    app = Flask(__name__)

    # key encrypt cookie
    app.config['SECRET_KEY'] = os.urandom(12).hex()

    app.config['MONGODB_SETTINGS'] = {
        'db': os.getenv("MONGO_DB"),
        'host': os.getenv("MONGO_HOST")
    }

    db.init_app(app)

    return app


