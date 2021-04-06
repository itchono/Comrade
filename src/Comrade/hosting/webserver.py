from flask import Flask, render_template, send_file, redirect, url_for
# used to create web server to keep bot actively hosted
from threading import Thread
# used to create separate parallel process to keep bot up

from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized

import os
import secrets

from utils.utilities import get_uptime, get_host
from utils.logger import logger
from client import client as bot
import datetime
from config import version, cfg
from db import collection

app = Flask('')

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = os.environ.get("CLIENTID")
app.config["DISCORD_CLIENT_SECRET"] = os.environ.get("CLIENTSECRET")
app.config["DISCORD_REDIRECT_URI"] = f"{cfg['Hosting']['host-url']}/callback"
app.config["DISCORD_BOT_TOKEN"] = os.environ.get("TOKEN")
app.config["SECRET_KEY"] = secrets.token_hex(20)

discordflask = DiscordOAuth2Session(app)

def divide_chunks(l, n):  
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 


@app.route('/')
def main():
    with open("comrade_primary.log", "r", encoding="utf-8") as f:
        content = f.read().splitlines()

    uptime = datetime.timedelta(seconds=round(get_uptime()))

    return render_template("index.html", uptime=str(uptime),
                           host=get_host(), numservers=len(bot.guilds),
                           user=str(bot.user), serverlist=[f"{server.name} "
                           f"({len(server.members)} members)"
                                                           for server in bot.guilds],
                           loglines=content,
                           version=version)


@app.route('/log')
def downloadFile():
    path = "comrade_full.log"
    return send_file(path, as_attachment=True,
                     attachment_filename='comrade_log.txt')


@app.route("/login/")
def login():
    return discordflask.create_session()


@app.route("/callback/")
def callback():
    discordflask.callback()
    return redirect(url_for(".emotegallery"))


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))


@app.route("/emotegallery/")
@requires_authorization
def emotegallery():
    user = discordflask.fetch_user()
    user.fetch_guilds()

    emote_urls = [{}]

    for g in user.guilds:
        for emote in collection("emotes").find({"server": g.id}):
            if len(emote_urls[-1]) >= 6:
                emote_urls.append({})
            emote_urls[-1][emote["name"]] = (emote["URL"], g.name, emote["type"])

    return render_template("emotegallery.html", images=emote_urls, username=user.name)


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.daemon = True
    server.start()
    logger.info("Flask server started.")


'''
Ping the url using something like https://uptimerobot.com/
This will keep things like repl.it up
'''
