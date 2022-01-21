# Comrade Requiem

**Comrade Requiem** AKA Comrade 6.0 is a full rewrite of Comrade Bot using the new `dis_snek` Discord library, in light of the old `discord.py` library being phased out. It features various modernizations throughout the codebase, and is designed to be a lot slimmer than 5.0.

![Image](https://pbs.twimg.com/media/D-u3WfZWwAAbNfJ.jpg)

## Key Differences from Comrade 5.0
- Full implementation of slash commands; message commands are no longer used.
    - When you use the bot, you no longer use a prefix, and instead use the `/` command.
    - Message functionality for some cases are still supported, including macros.
- New `dis_snek` library, which replaces the old `discord.py` library.
    - This library is more modern, and has a lot of improvements.
    - However, it is still in alpha, and may not be fully implemented.
- Slimmer codebase, with less features.
    - The codebase is much smaller, and is more focused on the core functionality of the bot.
    - Heavy functions such as graphing and latex rendering are no longer included.
- Modular design using hot-reloadable modules