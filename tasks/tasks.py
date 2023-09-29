import time
import logging
import threading

import json
from mcstatus import JavaServer
from pydactyl import PterodactylClient

logger = logging.getLogger("Tasks Worker")

# Read tasks config
logger.info("Reading tasks config...")
try:
    with open('tasks/config.json') as f:
        tasks_config = json.load(f)
except FileNotFoundError:
    logger.critical("Failed to read tasks config: File not found")
    exit(1)
except json.JSONDecodeError:
    logger.critical("Failed to read tasks config: Couldn't decode json")
    exit(1)

# Read pterodactyl key from file
logger.info("Reading Pterodactyl client key...")
try:
    with open('config/ptero.key') as f:
        pterodactyl_key = f.read()
except FileNotFoundError:
    logger.critical("Failed to read pterodactyl key: File not found")
    exit(1)
except json.JSONDecodeError:
    logger.critical("Failed to read pterodactyl key: Couldn't decode json")
    exit(1)

# Create a client to connect to the panel and authenticate with your API key.
logger.info("Connecting to panel...")
try:
    api = PterodactylClient(tasks_config['endpoint'], pterodactyl_key)
except:
    logger.critical("Failed to connect to panel, please check your config and network.")
    exit(1)


class OnlinePlayers(threading.Thread):
    def run(self):
        logger = logging.getLogger("Online Players")
        # Read the number of online players from a Minecraft server through network
        try:
            online_players = JavaServer.lookup(tasks_config['ping_host']).status().players.online
        except:
            logger.error("Failed to get online players from Minecraft server, please check your config file.")
            return
        logger.info("Get online players from Minecraft server: " + str(online_players))
        # Get Unix Timestamp as ms
        timestamp = int(round(time.time() * 1000))
        # Read online.json from static
        try:
            with open('static/online.json') as f:
                online_json = json.load(f)
        except FileNotFoundError:
            logger.error("Failed to read online.json: File not found")
            return
        except json.JSONDecodeError:
            logger.error("Failed to read online.json: Couldn't decode json")
            return
        # Add the new data to online.json
        online_json["online"].append([timestamp, online_players])
        # Write the new online.json
        try:
            with open('static/online.json', 'w') as outfile:
                json.dump(online_json, outfile)
        except FileNotFoundError:
            logger.error("Failed to write online.json: File not found")
            return


import json
import yaml


class ServersEdit(threading.Thread):
    def run(self):
        logger = logging.getLogger("Servers Edit")
        # Read the queue from file
        try:
            with open('queue/servers_edit.json') as f:
                queue = json.load(f)
            queue = queue["task"]
        except FileNotFoundError:
            logger.error("Failed to read queue file: File not found")
            return
        except json.JSONDecodeError:
            logger.error("Failed to read queue file: Couldn't decode json")
            return

        if len(queue) == 0:
            logger.info("Noting to do, queue is clean.")
            return

        # Get old config
        logger.debug("Get remote config...")
        try:
            config = yaml.load(api.client.servers.files.get_file_contents(tasks_config['server_id'], "config.yml").text,
                               Loader=yaml.FullLoader)
        except yaml.YAMLError:
            logger.error("Failed to get remote config: Yaml Error")
            return
        except:
            logger.error("Failed to get remote config")
            return

        while len(queue) != 0:
            first = queue[0]
            queue.pop(0)
            logger.info(f"Update server {first['server']} to {first['host']}")
            config["servers"][first["server"]]["address"] = first["host"]

        # Write the new config
        logger.debug("Write remote config...")
        try:
            api.client.servers.files.write_file(tasks_config['server_id'], "config.yml", yaml.dump(config))
        except:
            logger.error("Failed to write remote config")
            return

        # Clean the queue file
        try:
            with open('queue/servers_edit.json', 'w') as outfile:
                json.dump({"task": queue}, outfile)
        except FileNotFoundError:
            logger.error("Failed to clean queue file: File not found")
            return
        except:
            logger.error("Failed to clean queue file")


import json

class Restart(threading.Thread):
    def run(self):
        logger = logging.getLogger("Restart")
        # Read the queue from file
        try:
            with open('queue/restart.json') as f:
                queue = json.load(f)
        except:
            logger.error("Failed to read queue file, please check your filepack")
            return

        if not queue["restart"]:
            logger.info("No restarting request is queued.")
            return

        logger.info("Restarting server...")
        try:
            api.client.servers.send_power_action(tasks_config['server_id'], "restart")
        except:
            logger.error("Failed to restart server, please check your config file.")
            return
        queue["restart"] = False

        # Save the queue file
        try:
            with open('queue/restart.json', 'w') as outfile:
                json.dump(queue, outfile)
        except:
            logger.error("Failed to save queue file, please check your config file.")
            return
