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
mongo_client = MongoClient(os.environ.get('MONGOKEY'))
DB = mongo_client[mongo_client.list_database_names()[0]]
print(f"LEGACY: MongoDB Atlas Connected to Database: {mongo_client.list_database_names()[0]}")

'''
Favourites Interface
'''
def updateFavourite(imageID:str, imgurl:str, serverID, userID, category=""):
    favourites = DB.favourites

    thingy = {"imageID":imageID, "URL":imgurl, "server":serverID, "user":userID, "category":category}

    favourites.update({"imageID":imageID, "server":serverID, "user":userID, "category":category}, thingy, True)
    # (search target, info to put in, should we INSERT if no matching records are found?)

def allFavourites(serverID, userID, category=None):
    '''
    Returns a list of all favourited hentai images in given server
    '''
    favourites = DB.favourites

    if category: return list(favourites.find({"server":serverID, "user":userID, "category":category}))
    else: return list(favourites.find({"server":serverID, "user":userID}))

def getFavourite(serverID, imageID, userID, category=""):
    '''
    Returns a given favourite image
    '''
    favourites = DB.favourites

    return favourites.find_one({"server":serverID, "imageID":imageID, "user":userID, "category":category})

def removeFavourite(serverID, imageID, userID, category=""):
    '''
    Removes a given favourite image
    '''
    favourites = DB.favourites
    favourites.delete_one({"server":serverID, "imageID":imageID, "user":userID, "category":category})

