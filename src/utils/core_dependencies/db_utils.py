## Database utilities for Comrade
from cfg import *
from utils.startup import *

'''
General Database
'''

def DBcollection(collection):
    '''
    Returns the collection with the name
    '''
    try: return client.get_cog("Databases").DB[collection]
    except: return None

### CORE FUNCTIONS ###

def DBfind_one(collection, query):
    '''
    Retrieves a single document from the named collection
    '''
    return DBcollection(collection).find_one(query)

def DBfind(collection, query=None):
    '''
    Retrieves multiple documents from the named collection as a **list**.
    '''
    try: return list(DBcollection(collection).find(query))
    except: return None

def DBupdate(collection, query, data, upsert=True):
    '''
    Updates an entry, into a collection. Upserts by default.
    Upsert means: if the entry is not found, insert it instead.
    '''
    try: DBcollection(collection).update(query, data, upsert)
    except: pass

def DBremove_one(collection, query):
    '''
    Removes one entry from the collection with the given query
    '''
    try: DBcollection(collection).delete_one(query)
    except: pass

### OPS and THREATS ###

THREAT_CACHE = {}
OP_CACHE = {}

def getOPS(server):
    '''
    Gets the OPs in a server
    '''
    try:
        return OP_CACHE[server]
    except:
        OP_CACHE[server] = DBfind(USER_COL, {"OP": True, "server": server})
        return OP_CACHE[server]

def getThreats(server):
    '''
    Gets the threats in server using memoization system
    '''
    try:
        return THREAT_CACHE[server]
    except:
        THREAT_CACHE[server] = DBfind(USER_COL, {"threat-level": {"$gt": 0}, "server": server})
        return THREAT_CACHE[server]

### CFG Tools ###

def DBcfgitem(server, itemname):
    '''
    Retrieves an item from the user database
    '''
    try: return DBfind_one(SERVERCFG_COL, {"_id":server})[itemname]
    except: return 0

## User Tools ##

def DBuser(user_id, server_id):
    '''
    Retrieves a user from the database
    '''
    return DBfind_one(USER_COL, {"server":server_id, "user":user_id})

def updateDBuser(userdata):
    '''
    Updates a user in the database.
    '''
    if current_user := DBuser(userdata["user"], userdata["server"]):
        current_op, current_threat = current_user["OP"], current_user["threat-level"]

    DBupdate(USER_COL, {"server":userdata["server"], "user":userdata["user"]}, userdata)

    if current_user:
        # update caches on database 
        if current_op and current_op != userdata["OP"]: 
            OP_CACHE[userdata["server"]] = DBfind(USER_COL, {"OP": True, "server": userdata["server"]})
            print("Rebuild OP Cache")

        if current_threat and current_threat != userdata["threat-level"]: 
            THREAT_CACHE[userdata["server"]] = DBfind(USER_COL, {"threat-level": {"$gt": 0}, "server": userdata["server"]})
            print("Rebuild Threat Cache")
