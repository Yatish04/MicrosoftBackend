import pymongo
import pandas as pd 

df = pd.read_csv('finalausloc.csv')

url = "mongodb://yatishhr:skv5d9yiRMuHeS0ft5aYipjLAErgy0KEg5iacaWTWUW5JwdskJAlXVYZagWJfWD46ZILskdyxDWhtH2YXl7YdA==@yatishhr.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(url)
db = client.Azure
import pdb; pdb.set_trace()

lists=[]
for i in range(len(df)):
    temp={}
    temp["Disasterid"] = str(df.iloc[i]["Disasterid"])
    temp["Lat"] = str(df.iloc[i]["Lat"])
    temp["Long"] = str(df.iloc[i]["Long"])
    temp["facial"] = str(df.iloc[i]["facial"])
    temp["blobnames"] = str(df.iloc[i]["blobnames"])
    temp["issafe"] = str(df.iloc[i]["issafe"])
    temp["num_files"] = str(df.iloc[i]["num_files"])
    temp["numvictims"] = str(df.iloc[i]["numvictims"])
    temp["priority"] = str(df.iloc[i]["priority"])
    temp["user_id"] = str(df.iloc[i]["user_id"])
    temp["victims"] = str(df.iloc[i]["victims"])
    temp["medical"] = str(df.iloc[i]["medical"])
    db.Victim.insert(temp)
    lists.append(temp)

import pdb; pdb.set_trace()
db = client.Azure
# db.Victim.insert_many(lists)
pdb.set_trace()

# for i in range(len(df)):
#     temp={}
#     temp["Address"] = str(df.iloc[i]["Address"])
#     temp["City"] = str(df.iloc[i]["City"])
#     temp["Name"] = str(df.iloc[i]["Name"])
#     temp["items"] = str(df.iloc[i]["items"])
#     temp["phone_number"] = str(df.iloc[i]["phone_number"])
#     db.resources.insert(temp)


# for i in range(len(df)):
#     temp={}
#     temp["Address"] = str(df.iloc[i]["Address"])
#     temp["E-mail"] = str(df.iloc[i]["E-mail"])
#     temp["Name"] = str(df.iloc[i]["Name"])
#     temp["Password"] = str(df.iloc[i]["Password"])
#     temp["myresources"] = str(df.iloc[i]["myresources"])
#     db.ngo_data.insert(temp)