import json
import time
import traceback
import logging

logging.basicConfig(format='[%(asctime)s] [%(name)s / %(levelname)s] %(message)s', level=logging.NOTSET,
                    datefmt="%m-%d %H:%M:%S")

from tasks.tasks import *

logger = logging.getLogger("Main")

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
        elif pronlist[i].find("/") == 0:
            pronlist[i] = int(pronlist[i].replace("/", ""))
            if nowtime[i] % pronlist[i] == 0:
                match_count += 1
        else:
            pronlist[i] = int(pronlist[i])
            if nowtime[i] == pronlist[i]:
                match_count += 1
    if match_count == 4:
        return True
    else:
        return False


# Read worker config
try:
    with open('config/worker.json') as f:
        worker_config = json.load(f)
except FileNotFoundError:
    logger.critical("Failed to read worker config: File not found")
    exit(1)
except json.JSONDecodeError:
    logger.critical("Failed to read worker config: Cound not decode json")
    exit(1)

logger.info("Worker started, registered " + str(len(worker_config["tasks"])) + " tasks.")
while 1:
    for task in worker_config["tasks"]:
        if is_pron_match(task["pron"]):
            logger.info("Running task " + task["run"] + "...")
            try:
                eval(task["run"] + "().start()")
            except:
                traceback.print_exc()
                logger.error("Failed to run task " + task["run"] + ", please check the log.")
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Shutting down worker...")
        exit(0)
