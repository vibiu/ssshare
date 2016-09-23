import os
import sys
import socket
import signal
import json
# from datetime import datetime
from app import db
from app.models import SSUser
from manage import app

# class SSUser():
#     __tablename__ = 'ssusers'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.Unicode(64))
#     password = db.Column(db.Unicode(64))
#     email = db.Column(db.Unicode(64))
#     eduno = db.Column(db.Unicode(16))
#     port = db.Column(db.Unicode(5))
#     signup_time = db.Column(db.DateTime, default=datetime.now())
#     use_time = db.Column(db.DateTime, default=datetime.now())
#     method = db.Column(db.Unicode(16), default='aes-256-cfb')


CLIENT_SOCK = '/tmp/client3.sock'
# SERVER_SOCK = '/tmp/shadowsocks.sock'
SERVER_SOCK = '/tmp/shadowsocks.sock'


if os.path.exists(CLIENT_SOCK):
    os.remove(CLIENT_SOCK)
client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
client.bind(CLIENT_SOCK)
client.connect(SERVER_SOCK)


def parse_data(data=''):
    pass


def monitor():
    client.send(b'ping')
    print(client.recv(1506))
    with app.app_context():
        while True:
            data = client.recv(1506)
            data_dict = json.loads(data.decode('utf-8')[6:])
            for port, trans in data_dict.items():
                ssuser = SSUser.query.filter_by(port=port).first()
                if ssuser:
                    ssuser.transfer += trans
                    db.session.add(ssuser)
                    db.session.flush()
            db.session.commit()
            with open('data/monitor.log', 'a+') as moni:
                moni.write('transfering...\n{}\n'.format(data))


def write_pid_file():
    with open('data/ssshare.pid', 'w') as f:
        f.write('%s' % os.getpid())


def info():
    with open('data/ssshare.pid', 'r') as f:
        pid = f.read()
        print('pid: {}'.format(pid))


def start():
    pid = os.fork()
    if pid != 0:
        print('exit...\noperating on back.')
        os._exit(0)
    os.close(0)
    sys.stdin = open('data/stdin.log')
    os.close(1)
    sys.stdout = open('data/stdout.log', 'w')
    os.close(2)
    sys.stderr = open('data/stderr.log', 'w')
    os.setsid()
    os.umask(0)
    write_pid_file()
    monitor()


def end():
    with open('data/ssshare.pid', 'r') as f:
        pid = int(f.read())
    os.kill(pid, signal.SIGTERM)
    os.remove('data/ssshare.pid')
    print('killing pid: {}'.format(pid))


def main():
    if len(sys.argv) < 2 or sys.argv[1] == 'start':
        start()
    elif sys.argv[1] == 'info':
        info()
    else:
        end()

def test():
    def pings():
        client.send(b'ping')
        print(client.recv(1506))
    pings()
    # for i in range(100):
    #     pings()
    while True:
        print(client.recv(1506))

def insert_user():
    # print(dir(app))
    with app.app_context():
        ssuser = SSUser(
            username='admin',
            password='123456',
            port=8381,
        )
        db.session.add(ssuser)
        db.session.commit()


if __name__ == '__main__':
    # for i in range(10):
    #     client.send(b'ping')
    #     print(client.recv(1232))
    # monitor()
    main()
    # test()
    # insert_user()
