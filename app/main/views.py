from flask import jsonify
from flask import request, render_template, redirect, make_response, abort
from . import main
from .utils import pings, adduser, remove
from app.models import SSUser, db


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
            transfer=ssuser.transfer,
            method=ssuser.method,
            port=ssuser.port,
            password=ssuser.password
        ))
        resp.set_cookie('userid', username)
        return resp
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = request.form.get('code')
        print(code)
        if code != 'admincode':
            print('wrong code')
            return render_template('register.html')
        password = request.form.get('password')
        print(password)
        repassword = request.form.get('repassword')
        if password != repassword:
            print('w')
            return render_template('register.html')
        username = request.form.get('username')
        print(username)
        newuser = SSUser.query.filter_by(username=username).first()
        if newuser:
            print('a')
            return render_template('register.html')
        email = request.form.get('email')
        print(email)
        newuser = SSUser.query.filter_by(email=email).first()
        if newuser:
            print('h')
            return render_template('register.html')
        try:
            adduser(8383, password)
            port = 8383
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
                transfer=ssuser.transfer,
                method=ssuser.method,
                port=ssuser.port,
                password=ssuser.password
            ))
            resp.set_cookie('userid', username)
            return resp
    return render_template('register.html')


@main.route('/info', methods=['GET', 'POST'])
def info():
    userid = request.cookies.get('userid')
    if not userid:
        return redirect('/')
    ssuser = SSUser.query.filter_by(username=userid).first()
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


@main.route('/test', methods=['GET'])
def test():
    port_list = SSUser.query.order_by(SSUser.port).all()
    ports = [p.port for p in port_list]
    print(ports)
    return str(port_list)
