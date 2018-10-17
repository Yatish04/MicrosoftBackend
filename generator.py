import numpy as np
import pandas as pd
import random
import pymongo
num_samples = 1000

# max_lat = 13.165234
# min_lat = 12.736903

# max_long = 77.834417
# min_long = 77.380965

# lats=[]
# longs=[]
# for i in range(20000):
#     lat = random.uniform(min_lat,max_lat)
#     lats.append(lat)
# import random
# for i in range(20000):
#     long_= random.uniform(min_long,max_long)
#     longs.append(long_)

# df= pd.DataFrame()
# df["lat"] = lats
# df["long"] = longs

# mdf =pd.DataFrame()
# df = pd.read_csv('proper.csv')
# nums=0
# for i in np.unique(df['labels']):
#     lats = df[df['labels']==i]
#     if len(lats) >= 10:
#         mdf = pd.concat([mdf,lats],ignore_index=True)
#         nums+=1
 
#     if nums == 7:
#         break

# import pdb; pdb.set_trace()

li=[]
def get():
    js = {
        "user_id" : "0",
        "Lat" : "20.0756",
        "Long" : "28.95",
        "issafe" : "true",
        "Disasterid" : "0",
        "numvictims" : "7",
        "num_files" : 13,
        "blobnames" : [
            "03.jpg",
            "04.jpg",
            "05.jpg",
            "06.jpeg",
            "07.jpeg",
            "08.jpeg",
            "09.jpeg",
            "010.jpeg",
            "011.jpeg",
            "012.jpeg",
            "013.jpeg"
        ],
        "victims" : {
            "children" : 0,
            "elders" : 1,
            "female" : 0,
            "males" : 7
        },
        "priority" : 0
    }
    return js

df = pd.read_csv('properlatlongs.csv')

for i in range(len(df)):
    js = get()
    js["user_id"] = str(i)
    js["Lat"] = str(df.iloc[i]["lat"])
    js["Long"] = str(df.iloc[i]["long"])
    if df.iloc[i]["labels"] in [0,3,6]:
        print("he")
        js['issafe'] = "true"
    else:
        js["issafe"] = "false"
    js["victims"]["children"] = str(random.randint(0,2))
    js["victims"]["elders"] = str(random.randint(0,1))
    js["victims"]["female"] = str(random.randint(0,3))
    js["victims"]["males"] = str(random.randint(0,5))
    num_ = int(js["victims"]["children"])+int(js["victims"]["elders"]) + int(js["victims"]["female"]) + int(js["victims"]["males"])
    if js['issafe'] == 'true':
        js['priority'] = 0
    elif num_ <=2:
        js["priority"] = 0
    elif num_>2 and num_<=4:
        js["priority"] = 1
    else:
        js["priority"] = 2
    js["numvictims"] = num_
    li.append(js)

uri = "mongodb://yatish:O7EsukGSyf4XSr1rCo3QaskijO5KA5VoX2lPps9KM8eJVxKUdEg1KdcxvIYs9R1QsYRIq8oNf6E1osIshY3E2A==@yatish.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
db = client.Azure

import pdb; pdb.set_trace()

db.Victim.insert_many(li)
import pdb; pdb.set_trace()