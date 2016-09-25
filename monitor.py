import os
import sys
import time
import socket
import signal
import json
from datetime import datetime
from app import db
from app.models import SSUser
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
                moni.write(data.decode('utf-8'), '\n')
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
        ssuser = SSUser(
            username='admin',
            password='123456',
            port=8381,
        )
        db.session.add(ssuser)
        db.session.commit()
    print('insert admin ok.')


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
    else:
        end()


if __name__ == '__main__':
    main()
