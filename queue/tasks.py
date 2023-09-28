from

def queue_processer():
    # Read the queue from file
    try:
        with open('queue/servers_edit.json') as f:
            queue = json.load(f)
        queue = queue["task"]
    except:
        log("Failed to read queue file, please check your filepack")
        return

    if len(queue) == 0:
        log("Noting to do, queue is clean.")
        return
    
    # Get old config
    log("Get remote config...")
    try:
        config = yaml.load(api.client.servers.files.get_file_contents(worker_config['server_id'], worker_config['yaml_config_file']).text, Loader=yaml.FullLoader)
    except:
        log("Failed to get remote config, please check your config file.")
        return

    while len(queue) != 0:
        first = queue[0]
        queue.pop(0)
        log(f"Update server {first['server']} to {first['host']}")
        config["servers"][first["server"]]["address"] = first["host"]

    # Write the new config
    log("Write remote config...")
    try:
        api.client.servers.files.write_file(worker_config['server_id'], worker_config['yaml_config_file'], yaml.dump(config))
    except:
        log("Failed to write remote config, please check your config file.")
        return

    # Clean the queue file
    try:
        with open('queue/servers_edit.json', 'w') as outfile:
            json.dump({"task": queue}, outfile)
    except:
        log("Failed to clean queue file, please check your config file.")
        return

def online_json_processer():
    # Read the number of online players from a Minecraft server through network
    try:
        online_players = JavaServer.lookup("cp.rainplay.cn:20214").status().players.online
    except:
        log("Failed to get online players from Minecraft server, please check your config file.")
        return
    log("Get online players from Minecraft server: " + str(online_players))
    # Get Unix Timestamp as ms
    timestamp = int(round(time.time() * 1000))
    # Read online.json from static
    try:
        with open('static/online.json') as f:
            online_json = json.load(f)
    except:
        log("Failed to read online.json, please check your config file.")
        return
    # Add the new data to online.json
    online_json["online"].append([timestamp, online_players])
    # Write the new online.json
    try:
        with open('static/online.json', 'w') as outfile:
            json.dump(online_json, outfile)
    except:
        log("Failed to write online.json, please check your config file.")
        return