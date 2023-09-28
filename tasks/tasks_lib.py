import time

def log(string, origin = 'MAIN', level='INFO'):
    print(f"[{level} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] <{origin}> {string}")