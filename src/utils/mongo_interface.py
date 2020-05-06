'''
Comrade - Python-MongoDB Interfacer
'''

from pymongo import MongoClient
import json
import os
import dotenv

dotenv.load_dotenv()
client = MongoClient(os.environ.get('MONGOKEY'))
print("Atlas Cluster Connected, Running Version {}.".format(client.server_info()['version']))

def getUser(userID:int):
    '''
    gets a user based on user ID
    '''
    users = client['Comrade']['UserData']
    return users.find_one({"_id":userID})

def getUserfromNick(nickname:str):
    '''
    gets a user based on server nickname
    '''
    users = client['Comrade']['UserData']
    return users.find_one({"nickname":nickname})

def getCFG(serverID:int):
    '''
    Returns a dictionary with the cfg values for Comrade in a given server
    '''
    cfg = client['Comrade']['cfg']
    return cfg.find_one({"_id":serverID})

def updateCFG(newCFG:dict):
    '''
    Updates configuration file for a given server based on the ID
    '''
    print("cfgupdate call")
    cfg = client['Comrade']['cfg']
    cfg.update({"_id":newCFG["_id"]}, newCFG, True)

def updateUser(userData:dict):
    '''
    Upserts user into userData collection
    '''
    users = client.Comrade.UserData
    users.update({"_id":userData["_id"]}, userData, True) # upsert



