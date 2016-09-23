from . import db
from datetime import datetime


class SSUser(db.Model):
    __tablename__ = 'ssusers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(64))
    password = db.Column(db.Unicode(64))
    email = db.Column(db.Unicode(64))
    eduno = db.Column(db.Unicode(16))
    port = db.Column(db.Unicode(5))
    signup_time = db.Column(db.DateTime, default=datetime.now())
    use_time = db.Column(db.DateTime, default=datetime.now())
    method = db.Column(db.Unicode(16), default='aes-256-cfb')
    transfer = db.Column(db.Integer, default=0)
