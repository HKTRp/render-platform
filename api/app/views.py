from app import app, restfull_views, models, db
from flask import render_template, request

from app.forms import UploadForm


@app.route('/')
def projects_page():
    page = 1 if 'page' not in request.args else request.args['page']
    projects_obj = db.paginate(db.select(models.Project), page=page, per_page=20)
    projects = [{"title": proj.title, "status": proj.status,
                 "download": '/api/v1.0/projects/%d'
                             % proj.id if proj.status == restfull_views.ProjectStatus.RENDERED.value else ""}
                for proj in projects_obj]
    return render_template("projects.html", projects=projects, form=UploadForm())
