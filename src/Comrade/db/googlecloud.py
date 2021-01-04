'''
Google Cloud Storage Bucket for Comrade
'''
import os
from google.cloud import storage

from config import cfg

storage_client = None
bucket = None


def startup():
    '''
    Runs during startup to set up the databases
    The rationale is to defer execution until .env is loaded
    '''
    global storage_client, bucket
    # Ultra janky method of authenticating by pasting
    # JSON literal into the .env file :)
    with open("temp.json", "w") as f:
        f.write(os.environ.get("GC"))
    storage_client = storage.Client.from_service_account_json("temp.json")
    os.remove("temp.json")

    bucket = storage_client.get_bucket(cfg["GoogleCloud"]["bucket"])
    print(f"Google Cloud storage connected to: {bucket.name}")
