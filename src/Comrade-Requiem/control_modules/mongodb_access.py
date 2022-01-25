from pymongo import MongoClient
import os
from logger import log

try:
    _client = MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))
except Exception:
    log.critical("Could not connect to MongoDB. Check that you have dnspython installed.")
    log.exception("Could not connect to MongoDB")
else:
    log.info(f"Connected to MongoDB, detected DB {_client.list_database_names()[0]}")

def setup(bot):
    # Get first database in _client
    bot.db = _client[_client.list_database_names()[0]]
    log.info("Module mongodb_access.py loaded.")
