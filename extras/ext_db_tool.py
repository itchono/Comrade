from pymongo import MongoClient

import os, dotenv

# run in a live interpreter like Pyzo; have .env file ready

dotenv.load_dotenv()
mongo_client = MongoClient(os.environ.get('MONGOKEY'))
DB = mongo_client[mongo_client.list_database_names()[0]]
print(f"MongoDB Atlas Connected to Database: {mongo_client.list_database_names()[0]}")


## Refactor switcher

users = DB["UserData"]

for u in users.find(None):


    for field in list(u.keys())[:]:
        if " " in field:
            u[field.replace(" ", "-")] = u[field]

            del u[field]

    
    # users.update({"_id":u["_id"]}, u)
    print(u)

print("User Data has been refactored.")

cfg = DB["cfg"]
for u in cfg.find(None):

    yeet = []

    for field in list(u.keys())[:]:
        if " " in field:
            u[field.replace(" ", "-")] = u[field] 
            del u[field]
    print(u)