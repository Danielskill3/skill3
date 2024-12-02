from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse

username = urllib.parse.quote_plus("mosesmichael878")
password = urllib.parse.quote_plus("@13353Mike")

uri = f"mongodb+srv://{username}:{password}@cluster0.ubsrj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)