from utils.utilities import *


### CORE FUNCTIONS ###

def DBfind_one(collection, query):
    '''
    Retrieves a single document from the named collection
    '''
    try: return DBcollection(collection).find_one(query)
    except: return None

def DBfind(collection, query=None):
    '''
    Retrieves multiple documents from the named collection as a **list**.
    '''
    try: return list(DBcollection(collection).find(query))
    except: return None

def DBupdate(collection, query, data, upsert=True):
    '''
    Updates an entry, into a collection. Upserts by default.
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
        OP_CACHE[server] = DBfind(USER_COLLECTION, {"OP": True, "server": server})
        return OP_CACHE[server]

def getThreats(server):
    '''
    Gets the threats in server using memoization system
    '''
    try:
        return THREAT_CACHE[server]
    except:
        THREAT_CACHE[server] = DBfind(USER_COLLECTION, {"threat-level": {"$gt": 0}, "server": server})
        return THREAT_CACHE[server]

### CFG Tools ###

def DBcfgitem(server, itemname):
    '''
    Retrieves an item from the user database
    '''
    try: return DBfind_one(SERVERCFG_COLLECTION, {"_id":server})[itemname]
    except: return 0

## User Tools ##

def DBuser(user_id, server_id):
    '''
    Retrieves a user from the database
    '''
    return DBfind_one(USER_COLLECTION, {"server":server_id, "user":user_id})

def updateDBuser(userdata):
    '''
    Updates a user in the database.
    '''
    if current_user := DBuser(userdata["user"], userdata["server"]):
        current_op, current_threat = current_user["OP"], current_user["threat-level"]

    DBupdate(USER_COLLECTION, {"server":userdata["server"], "user":userdata["user"]})

    if current_user:
        # update caches on database 
        if current_op and current_op != userData["OP"]: 
            OP_CACHE[userData["server"]] = DBfind(USER_COLLECTION, {"OP": True, "server": userData["server"]})
            print("Rebuild OP Cache")

        if current_threat and current_threat != userData["threat-level"]: 
            THREAT_CACHE[userData["server"]] = DBfind(USER_COLLECTION, {"threat-level": {"$gt": 0}, "server": userData["server"]})
            print("Rebuild Threat Cache")
    

### NAMES OF EACH DB COLLECTION ###
USER_COLLECTION = "UserData"
SERVERCFG_COLLECTION = "cfg"
CUSTOMUSER_COLLECTION = "CustomUsers"
ANNOUNCEMENTS_COLLECTION = "announcements"