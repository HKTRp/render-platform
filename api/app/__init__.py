from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_httpauth import HTTPTokenAuth

from pymongo import MongoClient
import gridfs

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)

render_auth = HTTPTokenAuth(scheme='Bearer')

env_vars = dict(environ)

if environ['MONGO_USERNAME']:
    mongodb_connection = MongoClient(env_vars['MONGO_HOST'], int(env_vars['MONGO_PORT']),
                                     username=env_vars['MONGO_USERNAME'], password=env_vars['MONGO_PASSWORD'])
else:
    mongodb_connection = MongoClient(environ['MONGO_HOST'], int(environ['MONGO_PORT']))
grid_fs = gridfs.GridFS(mongodb_connection.grid_file)

from app import views, models

with app.app_context():
    db.create_all()
