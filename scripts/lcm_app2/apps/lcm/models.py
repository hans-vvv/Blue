from database.database import db


class Site(db.Model):
    __tablename__ = 'sites'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, unique=True)
