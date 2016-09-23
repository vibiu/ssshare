#! /usr/bin/env python
import os
import sys
import flask
import socket
import subprocess
from flask_script import Manager
# from bin.monitor import monitor
from app import db
from app import create_app
# from bin.monitor import start, end, info, remove, adduser
# from bin.monitor import SocketClient, ping
app = create_app('default')
manager = Manager(app)


@manager.command
def createall():
    db.create_all()


@manager.command
def dropall():
    db.dropall()


if __name__ == '__main__':
    manager.run()
    # remove(8382)
    # adduser(8383, 'testpswd')
