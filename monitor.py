import os
import sys
import time
import socket
import signal
import json
from datetime import datetime
from app import db
from app.models import SSUser
from app.main.utils import adduser
from manage import app


CLIENT_SOCK = '/tmp/client3.sock'
SERVER_SOCK = '/tmp/shadowsocks.sock'


if os.path.exists(CLIENT_SOCK):
    os.remove(CLIENT_SOCK)
client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
client.bind(CLIENT_SOCK)
client.connect(SERVER_SOCK)


def remove(port):
    data = 'remove: {"server_port": %d}' % port
    print(data)
    client.send(data.encode('utf-8'))
    message = client.recv(1506).decode('utf-8')
    print(message)
    return message


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

                    if ssuser.transfer > 10e7:
                        remove(ssuser.port)
                        ssuser.activate = False

                    db.session.add(ssuser)
                    db.session.flush()
            db.session.commit()
            with open('data/monitor.log', 'a+') as moni:
                moni.write('{}\n'.format(data.decode('utf-8')))
            # month clean
            now = datetime.now()
            if now.day == 1 and now.hour == 23 and now.minute == 59:
                time.sleep(2 * 60)
                for user in SSUser.query.all():
                    user.transfer = 0
                    if user.activate is False:
                        user.activate = True
                    db.session.add(user)
                    db.session.flush()
                db.session.commit()


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


def init():
    with app.app_context():
        adminssuser = SSUser(
            username='admin',
            password='adminpswd',
            port=8381,
        )
        testssuer = SSUser(
            username='test',
            password='testpswd',
            port=8382
        )
        db.session.add(adminssuser)
        db.session.add(testssuer)
        db.session.commit()
    print('insert admin ok.')


def update():
    with app.app_context():
        for user in SSUser.query.all():
            adduser(user.port, user.password)
            print('adding..' + user.port + ':' + user.username)


def end():
    with open('data/ssshare.pid', 'r') as f:
        pid = int(f.read())
    os.kill(pid, signal.SIGTERM)
    os.remove('data/ssshare.pid')
    print('killing pid: {}'.format(pid))


def test():
    def pings():
        client.send(b'ping')
        print(client.recv(1506))
    pings()
    # for i in range(100):
    #     pings()
    while True:
        print(client.recv(1506))


def main():
    if len(sys.argv) < 2 or sys.argv[1] == 'start':
        start()
    elif sys.argv[1] == 'info':
        info()
    elif sys.argv[1] == 'init':
        init()
    elif sys.argv[1] == 'update':
        update()
    else:
        end()


if __name__ == '__main__':
    main()
