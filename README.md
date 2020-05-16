# Comrade
Comrade is a Discord bot for my personal server, but available to use for anyone who

Check out the wiki page for more details!
https://github.com/itchono/Comrade/wiki

Thanks to https://github.com/seendsouza for hosting and deployment.

# Installation

## STAGE 1: Comrade Source Code

Clone the repo at https://github.com/itchono/Comrade/tree/Comrade-V3-dev

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
- log channel: 707709158933266503
- meme channel: 419214992517234728
- hentai channel: 558408620476203021
- emote directory: 669353887735611430
- vault channel: 587743411499565067

You must map each channel using
```
$c cfg "<channel name>" <channel id>
ex. $c cfg "vault channel" 587743411499565067
```
