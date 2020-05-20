from pymongo import MongoClient
import json
import os
import dotenv

'''
Comrade - Python-MongoDB Interfacer
'''

dotenv.load_dotenv()
client = MongoClient(os.environ.get('MONGOKEY'))
print("Atlas Cluster Connected, Running Version {}.".format(
    client.server_info()['version']))

def getUser(userID: int, serverID: int):
    '''
    gets a user based on user ID and guild ID.
    '''
    users = client['Comrade']['UserData']
    return users.find_one({"user": userID, "server": serverID})

def getUserfromNick(nickname: str, serverID: int):
    '''
    gets a user based on server nickname
    '''
    users = client['Comrade']['UserData']
    return users.find_one({"nickname": nickname, "server": serverID})

def userQuery(query: dict):
    '''
    Returns a set of users given a query
    '''
    users = client['Comrade']['UserData']
    return users.find(query)

def cfgQuery(query:dict):
    '''
    Returns a set of cfgs given a query
    '''
    cfg = client['Comrade']['cfg']
    return cfg.find(query)

def customUserQuery(query:dict):
    '''
    Returns a set of custom users given a query
    '''
    customs = client.Comrade.CustomUsers
    return customs.find(query)

def getCFG(serverID: int):
    '''
    Returns a dictionary with the cfg values for Comrade in a given server
    '''
    cfg = client['Comrade']['cfg']
    return cfg.find_one({"_id": serverID})

def updateCFG(newCFG: dict):
    '''
    Updates configuration file for a given server based on the ID
    '''
    cfg = client['Comrade']['cfg']
    cfg.update({"_id": newCFG["_id"]}, newCFG, True)

def updateUser(userData: dict):
    '''
    Upserts user into userData collection
    '''
    users = client.Comrade.UserData
    users.update({
        "user": userData["user"],
        "server": userData["server"]
    }, userData, True)  # upsert

def updateCustomUser(userData:dict):
    '''
    Upserts a custom user into userData collection
    '''
    customs = client.Comrade.CustomUsers
    customs.update({
        "name": userData["name"],
        "server": userData["server"]
    }, userData, True)  # upsert

def removeCustomUser(name, server):
    '''
    Removes a user from the collection
    '''
    customs = client.Comrade.CustomUsers
    return customs.find_one({"name": name, "server": server})


def getCustomUser(name, server):
    '''
    Gets a custom user from the database
    '''
    customs = client.Comrade.CustomUsers
    return customs.find_one({"name": name, "server": server})


def fillmodel(userID: int, serverID: int, model):
    '''
    Uploads a data model to Mongo.
    '''
    models = client.Comrade.NLPmodels
    models.update({
        "user": userID,
        "server": serverID
    }, {
        "user": userID,
        "server": serverID,
        "model": model
    }, True)  # upsert

def getmodel(userID: int, serverID: int):
    '''
    Gets a NLP model from the database.
    '''
    models = client.Comrade.NLPmodels
    return models.find_one({"user": userID, "server": serverID})

