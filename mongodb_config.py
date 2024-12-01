import ssl
from pymongo import MongoClient
from skill3.core.config import settings

def get_mongodb_client(mongo_uri=None):
    if not mongo_uri:
        mongo_uri = settings.MONGODB_URL
    
    client = MongoClient(
        mongo_uri,
        tls=True,
        tlsAllowInvalidCertificates=False,
        ssl_cert_reqs=ssl.CERT_REQUIRED,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000
    )
    return client

def get_database(db_name=None):
    if not db_name:
        db_name = settings.MONGODB_DB_NAME
    
    client = get_mongodb_client()
    return client[db_name]
