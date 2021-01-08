from flask import Flask, render_template, send_file
# used to create web server to keep bot actively hosted
from threading import Thread
# used to create separate parallel process to keep bot up

import logging
import os

from utils.utilities import get_uptime, get_host
from utils.logger import logger
from client import client as bot

# disable flask dumb logging
logging.getLogger('werkzeug').disabled = True
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

app = Flask('')


@app.route('/')
def main():
    return render_template("index.html", uptime=round(get_uptime()),
                           host=get_host(), numservers=len(bot.guilds),
                           user=str(bot.user))


@app.route('/log')
def downloadFile():
    path = "comrade.log"
    return send_file(path, as_attachment=True)


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()
    logger.info("Flask server started.")


'''
Ping the url using something like https://uptimerobot.com/
This will keep things like repl.it up
'''
