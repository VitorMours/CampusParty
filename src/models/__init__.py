from pymongo import MongoClient 

client = MongoClient(
    "mongodb+srv://vitormoura:32322916aA!@freecluster.pvx5mb0.mongodb.net/?appName=freeCluster",
    tls=True,
    tlsAllowInvalidCertificates=True
)

database = client.campus_party
collection = database.users
    
    