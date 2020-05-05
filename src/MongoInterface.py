'''
Comrade - Python-MongoDB Interfacer
'''

from pymongo import MongoClient
import json
import os
import dotenv

mClient = MongoClient(os.environ.get('MONGOKEY'))

def getUser(userID:int):
    users = mClient['Comrade']['UserData']

def updateUser(userData:dict):
    users = mClient['Comrade']['UserData']
    users.insert_one(userData)



