from time import time

from flask import Flask, request, redirect, session, render_template

from users import *
from servers import *
from interface import *

from mcstatus import JavaServer

DEBUG_MODE = False

app = Flask(__name__)

# Read secret key from file
with open('config/flask.key') as f:
    app.secret_key = f.read()

# Read site info from file
with open('config/siteinfo.json') as f:
    siteinfo = json.load(f)


# /
@app.route('/')
def root():
    if not login_status(session):
        return redirect('/login', code=302)
    return render_template(
        'index.html',
        siteinfo=siteinfo,
        username=session["username"],
        menus=render_menus(session),
        personalmenus=personalmenus
    )


# /tasks
@app.route('/tasks')
def tasks():
    if not login_status(session):
        return redirect('/login', code=302)
    if check_permission(session['username']) != 10:
        return redirect('/', code=302)
    return render_template(
        'tasks.html',
        siteinfo=siteinfo,
        username=session["username"],
        menus=render_menus(session),
        personalmenus=personalmenus,
        tasks=[
            {
                "name": "样例任务",
                "schedule": "Every Saturday 12:00",
                "type": "执行命令",
                "payload": "alert Hello World"
            }]
    )


# /servers
@app.route('/servers')
def servers():
    if not login_status(session):
        return redirect('/login', code=302)
    servers_list = get_servers(session['username'])
    return render_template(
        'servers.html',
        siteinfo=siteinfo,
        username=session["username"],
        menus=render_menus(session),
        personalmenus=personalmenus,
        servers=servers_list
    )


# /servers/edit
@app.route('/servers/edit', methods=['GET', 'POST'])
def servers_edit():
    if request.method == 'GET':
        srvname = request.values.get("id")
        if srvname is None:
            return "Bad request", 400
        if (check_permission(session['username']) != 10 and session['username'] not in get_server_by_name(srvname)[
            'owner']):
            return "Permission denied", 403
        if get_server_by_name(srvname) is None:
            return "服务器不存在", 404
        return render_template(
            'servers_edit.html',
            siteinfo=siteinfo,
            server=get_server_by_name(srvname),
        )
    elif request.method == 'POST':
        srvname = request.values.get("id")
        if srvname is None:
            return "Bad request", 400
        newhost = request.form['host']
        # Check if the user have permission to edit
        if (check_permission(session['username']) != 10 and session['username'] not in get_server_by_name(srvname)[
            'owner']):
            return "Permission denied", 403
        if not is_valid_host(newhost):
            return render_template(
                'servers_edit.html',
                siteinfo=siteinfo,
                server=get_server_by_name(srvname),
                message="请输入正确的服务器地址。"
            )
        # Update server information in database
        if update_server_by_name(srvname, newhost) is None:
            return render_template(
                'servers_edit.html',
                siteinfo=siteinfo,
                server=get_server_by_name(srvname),
                message="服务器不存在。"
            )
        # Read the queue file from queue/servers_edit.json
        with open('queue/servers_edit.json') as json_file:
            data = json.load(json_file)
        # Add the queue
        data['task'].append({
            "server": srvname,
            "host": newhost
        })
        # Save the queue file
        with open('queue/servers_edit.json', 'w') as outfile:
            json.dump(data, outfile)
        return redirect("/servers", code=302)


# /restart
@app.route('/restart', methods=['GET', 'POST'])
def restart():
    if not login_status(session):
        return redirect('/login', code=302)
    try:
        online_players = JavaServer.lookup(siteinfo['ping_host']).status().players.online
    except:
        online_players = "获取失败"
    with open('data/permissions.json') as json_file:
        data = json.load(json_file)
    if data[session['username']]['last_restart'] + 3600 * 24 > int(round(time())):  # 24 hours
        subtime = data[session['username']]['last_restart'] + 3600 * 24 - int(round(time()))
        avail = str(int(subtime / 60 / 60)) + " 小时 " + str(int(subtime / 60 % 60)) + " 分钟（您只能每隔 24 小时重启一次）"
    else:
        avail = "现在"
    if(request.method == 'GET'):
        return render_template(
            'restart.html',
            siteinfo=siteinfo,
            username=session["username"],
            menus=render_menus(session),
            personalmenus=personalmenus,
            servers=get_servers(session['username']),
            message=f"当前人数：{online_players}，下次可重启时间：{avail}"
        )
    elif(request.method == 'POST'):
        if(avail != "现在" or online_players != 0):
            return render_template(
                'restart.html',
                siteinfo=siteinfo,
                username=session["username"],
                menus=render_menus(session),
                personalmenus=personalmenus,
                servers=get_servers(session['username']),
                message="当前服务器在线人数不为 0 或距离上次重启不足 24 小时，无法重启。"
            )
        with open('data/permissions.json') as json_file:
            data = json.load(json_file)
        data[session['username']]['last_restart'] = int(round(time()))
        with open('data/permissions.json', 'w') as outfile:
            json.dump(data, outfile)
        with open('queue/restart.json') as json_file:
            data = json.load(json_file)
        data['restart'] = True
        with open('queue/restart.json', 'w') as outfile:
            json.dump(data, outfile)
        return render_template(
            'restart.html',
            siteinfo=siteinfo,
            username=session["username"],
            menus=render_menus(session),
            personalmenus=personalmenus,
            servers=get_servers(session['username']),
            message="已向队列工作进程发起重启请求"
        )

# /apikey
@app.route('/apikey')
def apikey():
    if not login_status(session):
        return redirect('/login', code=302)
    return render_template('apikey.html', siteinfo=siteinfo, username=session["username"], menus=render_menus(session))


# /login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if not session.get('username') is None:
            # The user has already logged in
            return redirect('/', code=302)
        # Return the login page
        return render_template('login.html', siteinfo=siteinfo)
    elif request.method == 'POST':
        # Proceed to login
        if request.form['username'] == "" or request.form['password'] == "":
            # Username or password is empty
            return render_template('login.html', siteinfo=siteinfo, message='用户名或密码不能为空。')
        username = request.form['username']
        shapass = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
        # Do login
        if do_login(username, shapass, session) == 0:
            return redirect('/', code=302)
        else:
            # Login failed
            return render_template('login.html', siteinfo=siteinfo, message='用户名或密码错误，请重试。')


# /changepass
@app.route('/changepass', methods=['GET', 'POST'])
def changepass():
    if not login_status(session):
        return redirect('/login', code=302)
    if request.method == 'GET':
        # Return the changepass page
        return render_template('changepass.html', siteinfo=siteinfo)
    elif request.method == 'POST':
        # Proceed to changepass
        if (request.form['old_password'] == "" or request.form['new_password'] == "" or request.form[
            'retype_password'] == ""):
            # Username or password is empty
            return render_template('changepass.html', siteinfo=siteinfo, message='密码不能为空。')
        if request.form['new_password'] != request.form['retype_password']:
            # Passwords don't match
            return render_template('changepass.html', siteinfo=siteinfo, message='两次输入的密码不一致。')
        if not is_valid_password(request.form['new_password']):
            # Passwords isn't valid
            return render_template('changepass.html', siteinfo=siteinfo,
                                   message='密码无效：长度至少为8为，不能包含除数字、字母、.和#以外的字符。')
        with open('data/users.json') as json_file:
            # Read the users file
            data = json.load(json_file)
        username = session['username']
        shapass = hashlib.sha256(request.form['old_password'].encode('utf-8')).hexdigest()
        # Find the user
        for user in data['users']:
            if user['username'] == username and user['password'] == shapass:
                user['password'] = hashlib.sha256(request.form['new_password'].encode('utf-8')).hexdigest()
                # Change successfully
                do_logout(session)
                # Save the users file
                with open('data/users.json', 'w') as outfile:
                    json.dump(data, outfile)
                return redirect('/login', code=302)
        else:
            # Change failed
            return render_template('changepass.html', siteinfo=siteinfo, message='旧密码错误，请重试。')


# /logout
@app.route('/logout')
def logout():
    do_logout(session)
    return redirect('/login', code=302)


# /favicon.ico
@app.route('/favicon.ico')
def favicon():
    # Return 404
    return "", 404


app.run(host='127.0.0.1', port=1356, debug=DEBUG_MODE)
