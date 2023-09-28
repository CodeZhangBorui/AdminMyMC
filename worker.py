import json
import time
import socket
import requests
import yaml
from pydactyl import PterodactylClient
from mcstatus import JavaServer

def log(string, level='INFO'):
    print(f"[{level} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] {string}")

# Read pterodactyl key from file
log("Reading config...")
try:
    with open('config/ptero.key') as f:
        pterodactyl_key = f.read()
except:
    log("Failed to read pterodactyl key, please check your key file.")
    exit(1)

# Read worker config
try:
    with open('config/worker.json') as f:
        worker_config = json.load(f)
except:
    log("Failed to read worker config, please check your config file.")
    exit(1)

# Create a client to connect to the panel and authenticate with your API key.
log("Connecting to panel...")
try:
    api = PterodactylClient(worker_config['endpoint'], pterodactyl_key)
except:
    log("Failed to connect to panel, please check your config and network.")
    exit(1)

log("Worker started")
worker_turn = 0
while(1):
    queue_processer()
    if(worker_turn % 12 == 0):
        online_json_processer()
    time.sleep(5)
    worker_turn += 1