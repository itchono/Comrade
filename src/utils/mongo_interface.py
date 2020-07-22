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
client = MongoClient(os.environ.get('MONGOKEY'))
DB = client[client.list_database_names()[0]]
print(f"MongoDB Atlas Connected to Database: {client.list_database_names()[0]}")


def DBuser(userID: int, serverID: int):
    '''
    gets a user based on user ID and guild ID.
    '''
    users = DB['UserData']
    return users.find_one({"user": userID, "server": serverID})

def getUserfromNick(nickname: str, serverID: int):
    '''
    gets a user based on server nickname
    '''
    users = DB['UserData']
    return users.find_one({"nickname": nickname, "server": serverID})

def userQuery(query: dict):
    '''
    Returns a set of users given a query
    '''
    users = DB['UserData']
    return users.find(query)

def cfgQuery(query:dict):
    '''
    Returns a set of cfgs given a query
    '''
    cfg = DB['cfg']
    return cfg.find(query)

def customUserQuery(query:dict):
    '''
    Returns a set of custom users given a query
    '''
    customs = DB["CustomUsers"]
    return customs.find(query)

def updateUser(userData: dict):
    '''
    Upserts user into userData collection
    '''
    users = DB["UserData"]

    if u := users.find_one({"user": userData["user"], "server": userData["server"]}):
        oldOP = u["OP"]
        oldTHREAT = u["threat-level"]

    users.update({
        "user": userData["user"],
        "server": userData["server"]
    }, userData, True)  # upsert

    if u:
        # Update caches, if the user exists
        if oldOP and oldOP != userData["OP"]: 
            OP_CACHE[userData["server"]] = list(userQuery({"OP": True, "server": userData["server"]}))
            print("Rebuild OP Cache")

        if oldTHREAT and oldTHREAT != userData["threat-level"]: 
            THREAT_CACHE[userData["server"]] = list(userQuery({"threat-level": {"$gt": 0}, "server": userData["server"]}))
            print("Rebuild Threat Cache")

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
def updateFavourite(imageID:str, imgurl:str, serverID):
    favourites = DB.favourites

    thingy = {"imageID":imageID, "URL":imgurl, "server":serverID}

    favourites.update({"imageID":imageID}, thingy, True)
    # (search target, info to put in, should we INSERT if no matching records are found?)

def allFavourites(serverID):
    '''
    Returns a list of all favourited hentai images in given server
    '''
    favourites = DB.favourites

    return list(favourites.find({"server":serverID}))

def getFavourite(serverID, imageID):
    '''
    Returns a given favourite image
    '''
    favourites = DB.favourites

    return favourites.find_one({"server":serverID, "imageID":imageID})

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
            updateUser(u)
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
                updateUser(u)
                return u[valuename]
            elif type(u[valuename]) == int:
                u[valuename] = int(value)
                updateUser(u)
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
                updateUser(u)
                return u[valuename]
        except:
            pass
