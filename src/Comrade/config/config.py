import configparser

from discord.file import File

'''
Loads the configuration file for Comrade.
If you are looking for the configuration file,
'''

try:
    with open("cfg.ini", "r") as f:
        pass
except FileNotFoundError:
    raise FileNotFoundError(
        "Config file not found. Please make sure cfg.ini exists.")

cfg = configparser.ConfigParser()
cfg.read("cfg.ini")
