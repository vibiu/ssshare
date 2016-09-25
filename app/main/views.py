from datetime import datetime, timedelta
import jwt
import base64
from flask import jsonify, current_app
from flask import request, render_template, redirect, make_response, abort
from . import main
from .utils import pings, adduser, remove
from app.models import SSUser, db


def idencode(username):
    return jwt.encode(
        {
            'username': username,
            'exp': datetime.now()
        },
        current_app.config['SECRET_KEY'],
        algorithm=current_app.config['APP_ALG'],
    )


def iddecode(encoded):
    try:
        decoded = jwt.decode(
            encoded,
            current_app.config['SECRET_KEY'],
            algorithms=[current_app.config['APP_ALG']],
        )
    except jwt.InvalidTokenError:
        return None
    return decoded


def bsencode(user):
    bsstring = 'aes-256-cfb:{}@{}:{}'.format(
        user.password, current_app.config['DEFAULT_IP'], user.port
    )
    return base64.b64encode(bsstring.encode('utf-8')).decode('utf-8')


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ssuser = SSUser.query.filter_by(username=username).first()
        if not ssuser:
            return redirect('/')
        if not ssuser.password == password:
            return redirect('/')
        resp = make_response(render_template(
            'info.html',
            ip=current_app.config['DEFAULT_IP'],
            transfer=ssuser.transfer,
            method=ssuser.method,
            port=ssuser.port,
            password=ssuser.password,
            bsstring=bsencode(ssuser)
        ))
        resp.set_cookie('userid', idencode(username))
        return resp
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = request.form.get('code')
        if code != 'admincode':
            return render_template('register.html')

        password = request.form.get('password')
        repassword = request.form.get('repassword')
        if password != repassword:
            return render_template('register.html')

        username = request.form.get('username')
        newuser = SSUser.query.filter_by(username=username).first()
        if newuser:
            return render_template('register.html')

        email = request.form.get('email')
        newuser = SSUser.query.filter_by(email=email).first()
        if newuser:
            return render_template('register.html')

        ports = [s.port for s in SSUser.query.all()]
        if not ports:
            port = current_app.config['DEFAUT_PORT']
        else:
            port = int(ports[-1]) + 1
        try:
            adduser(port, password)
        except Exception:
            abort(500)

        ssuser = SSUser(
            username=username,
            password=password,
            email=email,
            port=port
        )
        db.session.add(ssuser)
        db.session.commit()
        ssuser = SSUser.query.filter_by(username=username).first()
        if ssuser:
            resp = make_response(render_template(
                'info.html',
                ip=current_app.config['DEFAULT_IP'],
                transfer=ssuser.transfer,
                method=ssuser.method,
                port=ssuser.port,
                password=ssuser.password,
                bsstring=bsencode(ssuser)
            ))
            resp.set_cookie('userid', idencode(username))
            return resp
        else:
            abort(500)
    return render_template('register.html')


@main.route('/info', methods=['GET', 'POST'])
def info():
    userid = request.cookies.get('userid')
    if not userid:
        return redirect('/')

    decoded = iddecode(userid)
    if not decoded:
        return redirect('/')

    now = datetime.now()
    exp = datetime.fromtimestamp(decoded['exp'])
    last_time = current_app.config['AUTH_EXP']
    if now - exp + timedelta(hours=8) > timedelta(seconds=last_time):
        return redirect('/')
    else:
        username = decoded['username']

    ssuser = SSUser.query.filter_by(username=username).first()
    if not ssuser:
        return redirect('/')

    return render_template(
        'info.html',
        transfer=ssuser.transfer,
        method=ssuser.method,
        port=ssuser.port,
        password=ssuser.password
    )


@main.route('/ping', methods=['GET'])
def ping():
    ping_message = pings().decode('utf-8')
    return jsonify({'message': ping_message})


@main.route('/useradd', methods=['POST'])
def useradd():
    port = int(request.json.get('port'))
    password = request.json.get('password')
    message = adduser(port, password)
    return jsonify({'message': message})


@main.route('/remove', methods=['POST'])
def delete():
    port = int(request.json.get('port'))
    message = remove(port)
    return jsonify({'message': message})


@main.route('/ports', methods=['GET'])
def ports():
    ports = sorted([s.port for s in SSUser.query.all()])
    return str(ports)


@main.route('/tester', methods=['GET'])
def test():
    return render_template('test.html')
