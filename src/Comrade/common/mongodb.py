'''
MongoDB Interface for Comrade
'''
import sys
import os
import pymongo
from pymongo.collection import Collection

from common.config import cfg
from common.logger import logger

mongo_client = None
db = None


def setup(bot) -> None:
    # Entry point for extension
    '''
    Runs during startup to set up the databases
    The rationale is to defer execution until .env is loaded
    '''
    mongo_startup()


def mongo_startup():
    global mongo_client, db
    try:
        mongo_client = pymongo.MongoClient(os.environ.get("MONGOKEY"))
    except Exception:
        logger.critical("MongoDB Could not be connected. Check that you have "
                        "the correct MongoDB key in your .env file, and "
                        "the that you have dnspython installed"
                        "\nTerminating program...")
        sys.exit(1)  # Exit with error

    db = mongo_client[mongo_client.list_database_names()[0]]
    logger.info("MongoDB Atlas connected to: "
                f"{mongo_client.list_database_names()[0]}")


# Convenience method to return collection by name in configuration
def collection(name) -> Collection:
    if not db:
        mongo_startup()

    try:
        return db[cfg["MongoDB"][name]]
    except Exception:
        return None
