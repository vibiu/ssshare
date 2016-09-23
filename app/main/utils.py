import os
import socket
from flask import current_app

CLIENT_SOCK = '/tmp/client.sock'
SERVER_SOCK = '/tmp/shadowsocks.sock'

if os.path.exists(CLIENT_SOCK):
    os.remove(CLIENT_SOCK)
client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
client.bind(CLIENT_SOCK)
client.connect(SERVER_SOCK)


def pings():
    client.send(b'ping')
    message = client.recv(1506)
    return message


def adduser(port, password):
    data = 'add: {"server_port": %d, "password":"%s"}' % (port, password)
    client.send(data.encode('utf-8'))
    message = client.recv(1506).decode('utf-8')
    print(message)
    return message


def remove(port):
    data = 'remove: {"server_port": %d}' % port
    print(data)
    client.send(data.encode('utf-8'))
    message = client.recv(1506).decode('utf-8')
    print(message)
    return message
