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
    s += "Bot Stats:\nThreats: {0}\nKickList: {1}\nOPS: {2}\nLethality: {3}\nKick Requirement: {4}\nLast Daily: {5}\nSafe From Kick: {6}\nUser Banned Words: {7}".format(comrade_cfg.THREATS, 
    comrade_cfg.kickList, comrade_cfg.OPS, comrade_cfg.LETHALITY, comrade_cfg.KICK_REQ, comrade_cfg.LAST_DAILY, comrade_cfg.KICK_SAFE, comrade_cfg.USER_BANNED_WORDS)

    return s



def run():
    global t_start
    t_start = datetime.utcnow()
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
