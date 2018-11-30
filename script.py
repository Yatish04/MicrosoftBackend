import pymongo
import pandas as pd 

df = pd.read_csv('latest_ngo.csv')

url = "mongodb://yatishhr:pXYRVwZL2myXglrdgLSwAVKUb5U8AnbN1m83JXogbpKXlmwBBOdk4Py6s7EgBGsJoWRvTFJ6o7nNDY1n99HHMw==@yatishhr.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(url)
db = client.Azure

lists=[]
# for i in range(len(df)):
#     temp={}
#     temp["Disasterid"] = str(df.iloc[i]["Disasterid"])
#     temp["Lat"] = str(df.iloc[i]["Lat"])
#     temp["Long"] = str(df.iloc[i]["Long"])
#     temp["facial"] = str(df.iloc[i]["facial"])
#     temp["blobnames"] = str(df.iloc[i]["blobnames"])
#     temp["issafe"] = str(df.iloc[i]["issafe"])
#     temp["num_files"] = str(df.iloc[i]["num_files"])
#     temp["numvictims"] = str(df.iloc[i]["numvictims"])
#     temp["priority"] = str(df.iloc[i]["priority"])
#     temp["user_id"] = str(df.iloc[i]["user_id"])
#     temp["victims"] = str(df.iloc[i]["victims"])
#     db.Victim.insert(temp)
#     lists.append(temp)

# import pdb; pdb.set_trace()
# # db = client.Azure
# # db.Victim.insert_many(lists)
# pdb.set_trace()

# for i in range(len(df)):
#     temp={}
#     temp["Address"] = str(df.iloc[i]["Address"])
#     temp["City"] = str(df.iloc[i]["City"])
#     temp["Name"] = str(df.iloc[i]["Name"])
#     temp["items"] = str(df.iloc[i]["items"])
#     temp["phone_number"] = str(df.iloc[i]["phone_number"])
#     db.resources.insert(temp)


for i in range(len(df)):
    temp={}
    temp["Address"] = str(df.iloc[i]["Address"])
    temp["City"] = str(df.iloc[i]["City"])
    temp["Name"] = str(df.iloc[i]["Name"])
    temp["items"] = str(df.iloc[i]["items"])
    temp["phone_number"] = str(df.iloc[i]["phone_number"])
    db.resources.insert(temp)