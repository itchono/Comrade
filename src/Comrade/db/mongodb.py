'''
MongoDB Database for Comrade
'''
import sys
import os
import pymongo
from pymongo.collection import Collection

from config import cfg

mongo_client = None
db = None


def startup():
    '''
    Runs during startup to set up the databases
    The rationale is to defer execution until .env is loaded
    '''
    global mongo_client, db
    try:
        mongo_client = pymongo.MongoClient(os.environ.get("MONGOKEY"))
    except Exception:
        print("MongoDB Could not be connected. Check that you have "
              "the correct MongoDB key in your .env file, and "
              "the that you have dnspython installed"
              "\nTerminating program...")
        sys.exit(1)  # Exit with error

    db = mongo_client[mongo_client.list_database_names()[0]]
    print("MongoDB Atlas connected to: "
          f"{mongo_client.list_database_names()[0]}")

    # Scan collections to make sure they all exist, creating them if not
    for collection_name in cfg["MongoDB"]:
        try:
            _ = db[collection_name]
        except Exception:
            db.create_collection(collection_name)
            print("MONGODB: Create new collection in "
                  f"{mongo_client.list_database_names()[0]}:{collection_name}")


# Convenience method to return collection by name in configuration
def collection(name) -> Collection:
    try:
        return db[cfg["MongoDB"][name]]
    except Exception:
        return None
