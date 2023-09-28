import json
import time

import tasks.tasks_lib as tasks_lib
from tasks.tasks import *

def is_pron_match(pronstr):
    # Such as /5.*.*.*
    pronlist = pronstr.split(".")
    if len(pronlist) != 4:
        return None
    match_count = 0
    nowtime = [
        time.localtime().tm_sec,
        time.localtime().tm_min,
        time.localtime().tm_hour,
        time.localtime().tm_mday
    ]
    for i in range(4):
        if pronlist[i] == "*":
            match_count += 1
        elif(pronlist[i].find("/") == 0):
            pronlist[i] = int(pronlist[i].replace("/", ""))
            if(nowtime[i] % pronlist[i] == 0):
                match_count += 1
        else:
            pronlist[i] = int(pronlist[i])
            if(nowtime[i] == pronlist[i]):
                match_count += 1
    if(match_count == 4):
        return True
    else:
        return False

# Read worker config
try:
    with open('config/worker.json') as f:
        worker_config = json.load(f)
except:
    log("Failed to read worker config, please check your config file.")
    exit(1)

log("Worker started, registered " + str(len(worker_config["tasks"])) + " tasks.")
while(1):
    for task in worker_config["tasks"]:
        if(is_pron_match(task["pron"])):
            tasks_lib.log("Running task " + task["run"] + "...")
            try:
                eval(task["run"] + "().start()")
            except:
                tasks_lib.log("Failed to run task " + task["run"] + ", please check your config file.")
    time.sleep(0.5)