'''
Comrade - Python-MongoDB Interfacer
'''

from pymongo import MongoClient
import json
import os
import dotenv

dotenv.load_dotenv()
mClient = MongoClient(os.environ.get('MONGOKEY'))

def getUser(userID:int):
    users = mClient['Comrade']['UserData']
    return users.find_one({"_id":userID})

def updateUser(userData:dict):
    print("Attempting user push")
    print(mClient.list_database_names())
    users = mClient.Comrade.UserData
    
    users.insert_one(userData)



