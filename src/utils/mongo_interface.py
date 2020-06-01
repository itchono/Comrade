from pymongo import MongoClient
import json
import os
import dotenv
from polymorph.data_compressor import *

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

def fillcache(channelID, cache):
    '''
    Fills channel message cache
    '''
    channels = client.Comrade.ChannelCache
    channels.update({
        "_id": channelID,
    }, {"_id": channelID,
        "cache": cache
    }, True)  # upsert

def getcache(channelID):
    '''
    Tries to get message cache in list form.
    '''
    channels = client.Comrade.ChannelCache
    d = channels.find_one({"_id": channelID})
    if d: return decompressCache(d["cache"])
    return None

'''
Favourites Interface
'''

def updateFavourite(imageID:int, imgurl:str, serverID):
    favourites = client.Comrade.favourites

    thingy = {"imageID":imageID, "URL":imgurl, "server":serverID}

    favourites.update({"imageID":imageID}, thingy, True)
    # (search target, info to put in, should we INSERT if no matching records are found?)

def allFavourites(serverID):
    '''
    Returns a list of all favourited hentai images in given server
    '''
    favourites = client.Comrade.favourites

    return list(favourites.find({"server":serverID}))


'''
Specific I/O
'''

def userList(username, listname, value):
    pass
    #writes to user list

def togglebool(username, valuename):
    return "new value"
