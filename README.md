# Comrade 

![Comrade Logo](https://github.com/itchono/Comrade/blob/media/Media/Comrade%20New%20Logo%20May%202020.png)

![Publish Docker image](https://github.com/itchono/Comrade/workflows/Publish%20Docker%20image/badge.svg?branch=master)

Comrade is a Discord bot for my personal server, but available to use for anyone who would like a multipurpose bot!

Check out the wiki page for more details!
https://github.com/itchono/Comrade/wiki

## Inviting Comrade to your server
[Link to invite](https://discord.com/api/oauth2/authorize?client_id=707042278132154408&permissions=536083799&scope=bot)

NOTE: Self-hosting the bot is DEFINITELY better; using the above link should only be for provisional purposes.

# Installation

## STAGE 1: Comrade Source Code

Clone the repo at https://github.com/itchono/Comrade/

## STAGE 2: Install Requirements On Your Computer

In the root folder of the repository, run (from terminal or cmd):

```bash
pip install -r requirements.txt
```

Also make sure you are running Python 3.8+.

## STAGE 3: ENV file

Navigate to to /src and create a file called .env.

The contents of .env should look like:
```bash
TOKEN = yourbottoken
MONGOKEY = yourmongoconnectionstring
```

## STAGE 4: CFG file

Configure Comrade's local variables in src/cfg.py

## STAGE 5: Run

Run `main.py`. If the bot is being hosted on something like Heroku or Replit, and the `SELFPING_REQUIRED` setting is enabled, the bot will attempt to keep itself up 24/7.

# Adding/Updating Packages

1. Ensure the `pip-tools` package is installed on your system. If not, install it with `pip install pip-tools`.
2. Update the `requirements.in` with the names of the new packages you want to add. (optional)
3. Run `pip-compile requirements.in > requirements.txt`, or run `pip-compile requirements.in` and copy the output to replace the contents of `requirements.txt`.

# Database Requirements
Requires MongoDB Atlas [link to database; collections are automatically created.]

# Bot Setup
You will want to run a few key commmands upon adding the bot to your server.

```
$c resetcfg
$c reloadusers
```

These commands set the server-side configuration and user settings for the bot.

## Channel Mappings

Comrade relies on the server owner to feed text channels into Comrade for some of its funtionality.
This includes:
- announcements channel: A place for the bot to make announcements
- log channel: A place for the bot to log internal status
- meme channel: A place in which all newly posted image or videos are "reviewed"
- png channel: A channel to spawn pngs
- emote directory: A place where custom emotes are stored. Make this restricted such that only Comrade can post.
- vault channel: A place where users can vote to "pin" a message. Make this restricted such that only Comrade can post.
- custom-channel-group: (Optional) category under which custom channels can be created

You can map each channel using either ID (except for custom-channel-group), or by mention
```
$c cfg <channel name> <channel id>
ex. $c cfg vault-channel 587743411499565067
```

```
$c cfg <channel name> <channel mention>
ex. $c cfg "vault-channel" #meme-vault
```

# Changlog
Post-v3 Development
* 3.5 - Announcements system, refactoring
* 3.4 - Message triggers and other tweaks
* 3.3 - List Refactor + Minor Tweaks
* 3.2 - Database refactor
* 3.1 - Scripting System Added

v3 Developed from April - June 2020

Originally started in October 2019

# Credits
## Comrade Bot
Created by **Mingde Yin**

[GitHub](https://github.com/itchono)

With Help from:
* [Sean D'Souza](https://github.com/seendsouza)
* [Nuha Sahraoui](https://github.com/sunekku)
* [Victor Wang](https://github.com/vdoubleu)
* [Vimal Gunasegaran](https://github.com/slyflare)
* [Maggie Wang](https://github.com/mgwg)
* [Kevin Hu](https://github.com/kevzjhu)
* [Kevin Zhao](https://github.com/Kevinozoid)
* [Nick Hewko](https://github.com/NHewko)
* [Stephen Luu](https://github.com/PhtephenLuu)
* [Anthony Luo](https://github.com/4ntLu0)