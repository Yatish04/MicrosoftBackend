import pandas as pd 
import random
import pymongo

df = pd.read_csv('spotways_2018-07-10.csv',encoding='iso-8859-1')
uri = "mongodb://yatish:O7EsukGSyf4XSr1rCo3QaskijO5KA5VoX2lPps9KM8eJVxKUdEg1KdcxvIYs9R1QsYRIq8oNf6E1osIshY3E2A==@yatish.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
db = client.Azure


'''
format - 
    {
    "user_id":###,
    "lat":"12",
    "long":"124",
    "issafe":"",
    "numvictims":,
    "bloburls":[],
    }   
'''
df = df.sample(n=100)
df = df.reset_index()
list1=[]
for i in range(len(df)):
    temp={}
    temp["user_id"] = str(i)
    temp["Lat"] = str(df.iloc[i]["Lat"])
    temp["Long"] = str(df.iloc[i]["Long"])
    temp["issafe"] =  random.choice(["true","false"])
    temp["Disasterid"] = str(random.randrange(1,4))
    temp["numvictims"] = str(random.randint(0,10))
    temp["bloburls"] = ["https://rvsafeimages.blob.core.windows.net/imagescontainer/jpeg.jpg","https://rvsafeimages.blob.core.windows.net/imagescontainer/jpeg.jpg"]
    list1.append(temp)
import pdb; pdb.set_trace()
db.Victim.insert_many(list1)
import pdb; pdb.set_trace()
