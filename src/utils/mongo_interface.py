from pymongo import MongoClient
import json
import os
import dotenv
from polymorph.data_compressor import *

'''
Comrade - Python-MongoDB Interfacer
'''

THREAT_CACHE = {}
OP_CACHE = {}

dotenv.load_dotenv()
mongo_client = MongoClient(os.environ.get('MONGOKEY'))
DB = mongo_client[mongo_client.list_database_names()[0]]
print(f"LEGACY: MongoDB Atlas Connected to Database: {mongo_client.list_database_names()[0]}")

def updateCustomUser(userData:dict):
    '''
    Upserts a custom user into userData collection
    '''
    customs = DB["CustomUsers"]
    customs.update({
        "name": userData["name"],
        "server": userData["server"]
    }, userData, True)  # upsert

def removeCustomUser(name, server):
    '''
    Removes a user from the collection
    '''
    customs = DB["CustomUsers"]
    customs.delete_one({"name": name, "server": server})

def getCustomUser(name, server):
    '''
    Gets a custom user from the database
    '''
    customs = DB["CustomUsers"]
    return customs.find_one({"name": name, "server": server})

def fillcache(channelID, cache):
    '''
    Fills channel message cache
    '''
    channels = DB.ChannelCache
    channels.update({
        "_id": channelID,
    }, {"_id": channelID,
        "cache": cache
    }, True)  # upsert

def getcache(channelID):
    '''
    Tries to get message cache in list form.
    '''
    channels = DB.ChannelCache
    d = channels.find_one({"_id": channelID})
    if d: return decompressCache(d["cache"])
    return None

'''
Favourites Interface
'''
def updateFavourite(imageID:str, imgurl:str, serverID, userID):
    favourites = DB.favourites

    thingy = {"imageID":imageID, "URL":imgurl, "server":serverID, "user":userID}

    favourites.update({"imageID":imageID, "server":serverID, "user":userID}, thingy, True)
    # (search target, info to put in, should we INSERT if no matching records are found?)

def allFavourites(serverID, userID):
    '''
    Returns a list of all favourited hentai images in given server
    '''
    favourites = DB.favourites

    return list(favourites.find({"server":serverID, "user":userID}))

def getFavourite(serverID, imageID, userID):
    '''
    Returns a given favourite image
    '''
    favourites = DB.favourites

    return favourites.find_one({"server":serverID, "imageID":imageID, "user":userID})

'''
Commands
'''
def updateCmd(serverID:int, name:str, cmdText:str, cmdType:str):
    '''
    Updates a custom commands
    '''
    cfg = DB.CustomCommands

    thingy = {"server": serverID, "name":name, "cmd":cmdText, "type":cmdType}

    cfg.update({"server": serverID, "name":name}, thingy, True)
    # (search target, info to put in, should we INSERT if no matching records are found?)

def removeCmd(serverID:int, name:str):
    '''
    Removes a custom command
    '''
    cfg = DB.CustomCommands

    try:
        cfg.delete_one({"server": serverID, "name":name})
    except:
        pass

def getCmd(serverID: int, name : str):
    '''
    Gets a custom command.
    '''
    cfg = DB.CustomCommands

    if c := cfg.find_one({"server": serverID, "name":name}):
        return c["cmd"], c["type"]
    return None

def allcmds(serverID):
    '''
    Returns a list of all Cosmo Scripts in given server
    '''
    favourites = DB.CustomCommands
    return list(favourites.find({"server":serverID}))

'''
Specific I/O for lists and vars
'''
def getcustomList(serverID:int, listname):
    '''
    Reads a certain named list from the custom lists
    '''
    lists = DB.CustomLists

    try:
        return lists.find_one({"server": serverID, "name":listname})["list"]
    except:
        return None

def updatecustomList(serverID:int, listname, value):
    '''
    Writes to a certain named list from the custom lists
    '''
    lists = DB.CustomLists
    
    try:
        lists.update({"server": serverID, "name":listname}, {"server": serverID, "name":listname, "list":value}, True)
    except:
        pass
    
    return None

def listcustomLists(serverID: int):
    lists = DB.CustomLists
    return list(lists.find({"server": serverID}))

def removecustomList(serverID:int, listname):
    '''
    Removed a certain named list from the custom lists
    '''
    lists = DB.CustomLists
    
    try:
        lists.delete_one({"server": serverID, "name":listname})
    except:
        pass

def getuserList(userID: int, serverID:int, listname):
    '''
    Reads a certain named list from a user in the database
    '''
    try:
        u = DBuser(userID, serverID)[listname]
        return u if type(u) == list else None
    except:
        return None

def updateuserList(userID: int, serverID:int, listname, value):
    '''
    Writes to a certain named list from a user in the database
    '''
    if u := DBuser(userID, serverID):
        try:
            u[listname] = value
            updateDBuser(u)
            return 1
        except:
            pass
    
    return None

def setnum(userID: int, serverID:int, valuename, value):
    '''
    sets a numerical value for a user
    '''
    if u := DBuser(userID, serverID):
        try:
            if type(u[valuename]) == float: 
                u[valuename] = float(value)
                updateDBuser(u)
                return u[valuename]
            elif type(u[valuename]) == int:
                u[valuename] = int(value)
                updateDBuser(u)
                return u[valuename]
        except:
            pass

def togglebool(userID: int, serverID:int, valuename):
    '''
    Toggles a boolean for a user in the database
    '''
    if u := DBuser(userID, serverID):
        try:
            if type(u[valuename]) == bool:
                u[valuename] = not u[valuename] 
                updateDBuser(u)
                return u[valuename]
        except:
            pass
