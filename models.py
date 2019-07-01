import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    secret_number = db.Column(db.String, unique=False)
    password = db.Column(db.String)
    session_token = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return self.id
