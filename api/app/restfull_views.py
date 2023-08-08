import datetime

import flask
import pika
from os import environ

from werkzeug.utils import secure_filename

from app import app, models, db, grid_fs, render_auth
from flask import request

from enum import Enum

env_vars = dict(environ)


class ProjectStatus(Enum):
    LOADING = "LOADING"
    LOADED = "LOADED"
    RENDERING = "RENDERING"
    RENDERED = "RENDERED"
    FAILED = "FAILED"


@render_auth.verify_token
def verify_token(token):
    if token == env_vars['RENDER_AUTH_TOKEN']:
        return 'render'


def save_project_file(filename, file):
    grid_fs.put(file, filename=filename)


def add_request_to_query(filename):
    credentials = pika.PlainCredentials(env_vars['RABBIT_USERNAME'], env_vars['RABBIT_PASSWORD'])
    with pika.BlockingConnection(pika.ConnectionParameters(env_vars['RABBIT_HOST'],
                                                           port=int(env_vars['RABBIT_PORT']),
                                                           credentials=credentials)) as connection:
        with connection.channel() as rabbit_channel:
            rabbit_channel.queue_declare('OnRender')
            rabbit_channel.basic_publish(exchange='', routing_key="OnRender", body=filename)


def handle_loading_request(filename, project_id, proj):
    save_project_file(filename, proj)
    with app.app_context():
        project = db.get_or_404(models.Project, project_id)
        project.loaded_date = datetime.datetime.utcnow()
        project.status = ProjectStatus.LOADED.value
        db.session.commit()
    add_request_to_query(filename)


@app.route('/api/v1.0/projects/', methods=['POST'])
def load_project():
    proj = request.files['projfile']
    sec_fn = secure_filename(proj.filename)
    if not sec_fn.endswith(".zip"):
        return "", 415
    project = models.Project(title=sec_fn, status=ProjectStatus.LOADING.value)
    db.session.add(project)
    db.session.commit()
    filename = '%d/%s' % (project.id, sec_fn)
    handle_loading_request(filename, project.id, proj)
    return "ok"


@app.route('/api/v1.0/projects/<int:project_id>', methods=['GET'])
def download_project(project_id):
    filename = '%d/rendered.zip' % project_id
    file = grid_fs.find_one({"filename": filename})
    return flask.send_file(file, download_name="rendered.zip")


@render_auth.login_required
@app.route('/api/v1.0/projects/<int:project_id>/status', methods=['PATCH'])
def change_project_status(project_id):
    new_status = request.json['status']
    try:
        ProjectStatus(new_status)
        project = db.get_or_404(models.Project, project_id)
        project.status = new_status
        db.session.commit()
        return "", 200
    except ValueError:
        return "", 400
