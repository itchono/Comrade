# Comrade 

![Comrade Logo](res/Comrade_logo.png)

![Publish Docker image](https://github.com/itchono/Comrade/workflows/Publish%20Docker%20image/badge.svg?branch=master)

Comrade is a Discord bot for my personal server, but available to use for anyone who would like a multipurpose bot!
Comrade is written mainly in Python using `discord.py`, and partially in Go using `discordgo`. Comrade uses MongoDB and Google Cloud Storage for persistence.

Comrade provides a multitude of different features, and includes many features that I have liked from other bots. I created Comrade with the purpose of being able to fine-tune these features to the way I want, and have full control over what the bot does.

I started Comrade as a way to learn Python, and with every rewrite I've put in more and more of my new skills. I am still learning, so of course the code, as well as the repo will be a bit messy.

# Inviting Comrade to your server
[Link to invite](https://discord.com/api/oauth2/authorize?client_id=707042278132154408&permissions=536083799&scope=bot)

NOTE: Self-hosting the bot is DEFINITELY better; using the above link should only be for provisional purposes.

# Adding/Updating Packages
If you are contributing, and would like to add a new library to the Python code, please make sure you add it to `requirements.in`. You will then need to update `requirements.txt`, following the below steps.

1. Ensure the `pip-tools` package is installed on your system. If not, install it with `pip install pip-tools`.
2. Update the `requirements.in` with the names of the new packages you want to add. (optional)
3. Run `pip-compile requirements.in > requirements.txt`, or run `pip-compile requirements.in` and copy the output to replace the contents of `requirements.txt`.

# Timeline
I first started coding in Python in September 2019, so the early troubles I had with the bot were consequences of the limitation of my experience. As I picked up new skills, I have rewritten the bot several times over.

* V1 Originally started in October 2019 as a bot for my Discord server; code was crudely written, all in one big file.
* V2 Full rewrite of bot in December 2019-Jan 2020, using proper format for commands; implemented lots of new features, but code got very messy since it was still all one big file.
* V3 Full rewrite of bot in April-Jun 2020, using multiple files and Discord Cogs. Implemented databases, so that the bot's information could be persisted across multiple hosts.
* V4 Major Feature Update in Oct 2020, updating several modules to work better.
* V5 Full rewrite of bot with more care to code quality, rewriting many modules from scratch to make the code more accessible to everyone.

# Credits
## Comrade Bot
Created by [**Mingde Yin**](https://github.com/itchono) - Project Lead

With Help from:
* [Sean D'Souza](https://github.com/seendsouza) - DevOps and Mentoring
* [Nuha Sahraoui](https://github.com/sunekku) - NSFW module
* [Victor Wang](https://github.com/vdoubleu) - Custom Coding Language Module
* [Vimal Gunasegaran](https://github.com/slyflare) - Emote system, general features
* [Maggie Wang](https://github.com/mgwg) - General features and testing
* [Kevin Hu](https://github.com/kevzjhu) - General features and testing
* [Kevin Zhao](https://github.com/Kevinozoid) - Feature suggestions and testing
* [Nick Hewko](https://github.com/NHewko) - Feature suggestions and testing
* [Stephen Luu](https://github.com/PhtephenLuu) - Feature suggestions and testing
* [Anthony Luo](https://github.com/4ntLu0) - Feature suggestions and testing
