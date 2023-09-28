import json
import hashlib

# Do login function
def do_login(username, shapass, session):
    # Read the users file
    with open('data/users.json') as json_file:
        data = json.load(json_file)
    # Find the user
    for user in data['users']:
        if(user['username'] == username and user['password'] == shapass):
            # Login successfully
            session['username'] = username
            session['token'] = hashlib.sha256(shapass.encode('utf-8')).hexdigest()
            return 0
    return 65001

# Do logout function
def do_logout(session):
    session.pop('username', None)
    session.pop('token', None)

# Login status check function
def login_status(session):
    if(session.get('username') is None or session.get('token') is None):
        do_logout(session)
        return False
    else:
        # Read the users file
        with open('data/users.json') as json_file:
            data = json.load(json_file)
        # Find the user
        for user in data['users']:
            if(user['username'] == session['username'] and hashlib.sha256(user['password'].encode('utf-8')).hexdigest() == session['token']):
                return True
        do_logout(session)
        return False

# Get user permission function
def check_permission(username):
    # Read the permission file
    with open('data/permissions.json') as json_file:
        data = json.load(json_file)
    if(data[username]['banned'] == True):
        return 0
    elif(data[username]['admin'] == True):
        return 10
    else:
        return 1

# Check if the password is strong enough
def is_valid_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False

    # Check if the password contains only digits, letters, '.', and '#'
    for c in password:
        if not c.isdigit() and not c.isalpha() and c not in ('.', '#'):
            return False

    # If the password passes all checks, it is valid
    return True