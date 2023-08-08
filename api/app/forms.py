from wtforms import Form
from wtforms import FileField
from wtforms.validators import InputRequired


class UploadForm(Form):
    project_file = FileField("proj_file", validators=[InputRequired()])
