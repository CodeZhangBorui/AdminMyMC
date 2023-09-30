import json
import hashlib

new_user = input("新用户名 > ")
new_pass = input("新密码 > ")
new_admin = input("是否为管理员？(y/n) > ")
new_banned = input("是否封禁？(y/n) > ")

# Read the users file
with open('data/users.json') as json_file:
    data = json.load(json_file)

# Add the new user
data['users'].append({
    "username": new_user,
    "password": hashlib.sha256(new_pass.encode('utf-8')).hexdigest(),
})

# Write the users file
with open('data/users.json', 'w') as outfile:
    json.dump(data, outfile)

if new_admin == "y":
    new_admin = True
else:
    new_admin = False

if new_banned == "y":
    new_banned = True
else:
    new_banned = False

# Read the permissions file
with open('data/permissions.json') as json_file:
    data = json.load(json_file)

# Add the new user
data[new_user] = {
    "admin": new_admin,
    "banned": new_banned,
    "last_restart": 0
}

# Write the permissions file
with open('data/permissions.json', 'w') as outfile:
    json.dump(data, outfile)

print("用户创建成功。")
