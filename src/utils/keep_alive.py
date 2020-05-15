from flask import Flask, render_template
from threading import Thread
from datetime import datetime

import logging
import os

logging.getLogger('werkzeug').disabled = True
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

t_start = 0

app = Flask('')

@app.route('/')
def main():
    return 'Comrade BOT is online - Uptime: {}'.format(datetime.utcnow() - t_start)

def run():
    global t_start
    t_start = datetime.utcnow()
    app.run(host="0.0.0.0", port=8080,)

def keep_alive():
    server = Thread(target=run)
    server.start()

def shutdown():
    server = Thread(target=run)
    server._stop()
