from .tasks_lib import *
import threading

import json
from mcstatus import JavaServer
from pydactyl import PterodactylClient

# Read tasks config
log("Reading tasks config...", origin="SERVERS_EDIT")
try:
    with open('tasks/config.json') as f:
        tasks_config = json.load(f)
except:
    log("Failed to read tasks config, please check your config file.", origin="SERVERS_EDIT")
    exit(1)

# Read pterodactyl key from file
log("Reading Pterodactyl client key...", origin="SERVERS_EDIT")
try:
    with open('config/ptero.key') as f:
        pterodactyl_key = f.read()
except:
    log("Failed to read pterodactyl key, please check your key file.", origin="SERVERS_EDIT")
    exit(1)

# Create a client to connect to the panel and authenticate with your API key.
log("Connecting to panel...", origin="SERVERS_EDIT")
try:
    api = PterodactylClient(tasks_config['endpoint'], pterodactyl_key)
except:
    log("Failed to connect to panel, please check your config and network.", origin="SERVERS_EDIT")
    exit(1)

class online_players(threading.Thread):
    def run(self):
        # Read the number of online players from a Minecraft server through network
        try:
            online_players = JavaServer.lookup(tasks_config['ping_host']).status().players.online
        except:
            log("Failed to get online players from Minecraft server, please check your config file.", origin="ONLINE_PLAYERS")
            return
        log("Get online players from Minecraft server: " + str(online_players), origin="ONLINE_PLAYERS")
        # Get Unix Timestamp as ms
        timestamp = int(round(time.time() * 1000))
        # Read online.json from static
        try:
            with open('static/online.json') as f:
                online_json = json.load(f)
        except:
            log("Failed to read online.json, please check your config file.", origin="ONLINE_PLAYERS")
            return
        # Add the new data to online.json
        online_json["online"].append([timestamp, online_players])
        # Write the new online.json
        try:
            with open('static/online.json', 'w') as outfile:
                json.dump(online_json, outfile)
        except:
            log("Failed to write online.json, please check your config file.", origin="ONLINE_PLAYERS")
            return

import json
import yaml

class servers_edit(threading.Thread):
    def run(self):
        # Read the queue from file
        try:
            with open('queue/servers_edit.json') as f:
                queue = json.load(f)
            queue = queue["task"]
        except:
            log("Failed to read queue file, please check your filepack", origin="SERVERS_EDIT")
            return

        if len(queue) == 0:
            log("Noting to do, queue is clean.", origin="SERVERS_EDIT")
            return
        
        # Get old config
        log("Get remote config...", origin="SERVERS_EDIT")
        try:
            config = yaml.load(api.client.servers.files.get_file_contents(tasks_config['server_id'], "config.yml").text, Loader=yaml.FullLoader)
        except:
            log("Failed to get remote config, please check your config file.", origin="SERVERS_EDIT")
            return

        while len(queue) != 0:
            first = queue[0]
            queue.pop(0)
            log(f"Update server {first['server']} to {first['host']}", origin="SERVERS_EDIT")
            config["servers"][first["server"]]["address"] = first["host"]

        # Write the new config
        log("Write remote config...", origin="SERVERS_EDIT")
        try:
            api.client.servers.files.write_file(tasks_config['server_id'], "config.yml", yaml.dump(config))
        except:
            log("Failed to write remote config, please check your config file.", origin="SERVERS_EDIT")
            return

        # Clean the queue file
        try:
            with open('queue/servers_edit.json', 'w') as outfile:
                json.dump({"task": queue}, outfile)
        except:
            log("Failed to clean queue file, please check your config file.", origin="SERVERS_EDIT")
            return

import json

class restart(threading.Thread):
    def run(self):
        # Read the queue from file
        try:
            with open('queue/restart.json') as f:
                queue = json.load(f)
        except:
            log("Failed to read queue file, please check your filepack", origin="SERVERS_EDIT")
            return

        if queue["restart"] == False:
            log("No restarting request is queued.", origin="RESTART")
            return
        
        log("Restarting server...", origin="RESTART")
        try:
            api.client.servers.send_power_action(tasks_config['server_id'], "restart")
        except:
            log("Failed to restart server, please check your config file.", origin="RESTART")
            return
        queue["restart"] = False

        # Save the queue file
        try:
            with open('queue/restart.json', 'w') as outfile:
                json.dump(queue, outfile)
        except:
            log("Failed to save queue file, please check your config file.", origin="RESTART")
            return