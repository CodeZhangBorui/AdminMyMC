import json
import re

from users import *


# Check if the string is a valid host
def is_valid_host(input_string):
    # 定义正则表达式模式，用于匹配IP地址、IP地址加端口、域名和域名加端口
    pattern = r'^(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d{1,5})?|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?::\d{1,5})?)$'
    # 使用正则表达式匹配输入字符串
    return bool(re.match(pattern, input_string))


# Get user servers list
def get_servers(username):
    # Read the servers file
    with open('data/servers.json') as json_file:
        data = json.load(json_file)
    if check_permission(username) == 10:
        return data['servers']
    servers = []
    for server in data['servers']:
        # the server['owner'] contains username
        if username in server['owner']:
            servers.append(server)
    return servers


# Get server information by name
def get_server_by_name(server_name):
    # Read the servers file
    with open('data/servers.json') as json_file:
        data = json.load(json_file)
    for server in data['servers']:
        if server['name'] == server_name:
            return server
    return None


# Update server information by name
def update_server_by_name(server_name, newhost):
    # Read the servers file
    with open('data/servers.json') as json_file:
        data = json.load(json_file)
    for server in data['servers']:
        if server['name'] == server_name:
            server['host'] = newhost
            # Write the servers file
            with open('data/servers.json', 'w') as outfile:
                json.dump(data, outfile)
            return 0
    return None
