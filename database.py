import pymongo


client = pymongo.MongoClient('mongodb://root:example@127.0.0.1:27017/')

# Create or access a database
mydb = client["tulip"]

# Create or access a collection (similar to a table in SQL databases)
mycol = mydb["schedule"]

todotable = mydb["todo"]
