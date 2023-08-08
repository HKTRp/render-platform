from app import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    loaded_date = db.Column(db.DateTime, index=True)
    rendered_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(16))

    def __repr__(self):
        return '<Project %r>' % self.title
