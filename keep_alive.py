from flask import Flask
from threading import Thread
import comrade_cfg
from datetime import datetime

t_start = 0

app = Flask('')

@app.route('/')
def main():
    # debug info

    # config status
    s = 'Comrade BOT is online\n'
    s += "Uptime: {}\n".format(datetime.utcnow() - t_start)
    return s



def run():
    global t_start
    t_start = datetime.utcnow()
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
