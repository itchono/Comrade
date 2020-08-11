# Comrade 

![Comrade Logo](https://github.com/itchono/Comrade/blob/media/Media/Comrade%20New%20Logo%20May%202020.png)

![Publish Docker image](https://github.com/itchono/Comrade/workflows/Publish%20Docker%20image/badge.svg?branch=master)

Comrade is a Discord bot for my personal server, but available to use for anyone who would like a multipurpose bot!

Check out the wiki page for more details!
https://github.com/itchono/Comrade/wiki

Thanks to https://github.com/seendsouza for hosting and deployment.

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
# Adding/Updating Packages

1. Ensure the `pip-tools` package is installed on your system. If not, install it with `pip install pip-tools`.
2. Update the `requirements.in` with the names of the new packages you want to add. (optional)
3. Run `pip-compile requirements.in > requirements.txt`, or run `pip-compile requirements.in` and copy the output to replace the contents of `requirements.txt`.

# Bot Setup

You will want to run a few key commmands upon adding the bot to your server.

```
$c resetcfg
$c reloadusers
```

These commands set the server-side configuration and user settings for the bot.

## Channel-Mappings

Comrade relies on the server owner to feed text channels into Comrade for some of its funtionality.
This includes:
- announcements channel: A place for the bot to make announcements
- log channel: A place for the bot to log internal status
- meme channel: A place in which all newly posted image or videos are "reviewed"
- hentai channel: A channel for Comrade's Hentai Module
- emote directory: A place where custom emotes are stored. Make this restricted such that only Comrade can post.
- vault channel: A place where users can vote to "pin" a message. Make this restricted such that only Comrade can post.

You must map each channel using
```
$c cfg "<channel name>" <channel id>
ex. $c cfg "vault channel" 587743411499565067
```
