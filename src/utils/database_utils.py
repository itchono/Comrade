from utils.utilities import *


### CORE FUNCTIONS ###

def DBfind_one(collection, query):
    '''
    Retrieves a single document from the named collection
    '''
    try: return DBcollection(collection).find_one(query)
    except: return None

def DBfind(collection, query):
    '''
    Retrieves multiple documents from the named collection as a list.
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

### SPECIFICS ###


### NAMES OF EACH DB COLLECTION ###
USER_COLLECTION = "UserData"
SERVERCFG_COLLECTION = "cfg"