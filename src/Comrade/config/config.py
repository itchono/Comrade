import configparser

'''
Loads the configuration file for Comrade.
If you are looking for the configuration file,
it is located in the root directory (src/Comrade).
'''

cfg = configparser.ConfigParser()
cfg.read("cfg.ini")
