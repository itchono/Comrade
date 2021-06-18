import configparser

# Loads the configuration file for Comrade.


try:
    with open("cfg.ini", "r") as f:
        pass
except FileNotFoundError:
    raise FileNotFoundError(
        "Config file not found. Please make sure cfg.ini exists.")

cfg = configparser.ConfigParser()
cfg.read("cfg.ini")

with open("VERSION", "r", encoding="utf-8") as f:
    version = f.read()

def setup(bot):
    # Entry point for extension
    pass
