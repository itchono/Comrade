from google.cloud import storage
from google.oauth2 import service_account


storage_client = storage.Client.from_service_account_json("rational-armor-294302-9eb184943c69.json")

bucket = storage_client.get_bucket('comrade_emotes')

for file in storage_client.list_blobs(bucket):
    print(file.media_link)

