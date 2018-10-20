#import urllib3
from bs4 import BeautifulSoup
from bson import ObjectId   
import requests,PyPDF2, io
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
#import pdb
from flask import *
from azure.storage.blob import BlockBlobService, PublicAccess
import json
# import matplotlib.pyplot as plt
# from PIL import Image
# from matplotlib import patches
from io import BytesIO
import random
import pymongo

uri = "mongodb://yatish:O7EsukGSyf4XSr1rCo3QaskijO5KA5VoX2lPps9KM8eJVxKUdEg1KdcxvIYs9R1QsYRIq8oNf6E1osIshY3E2A==@yatish.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
db = client.Azure

she_url = "mongodb://kitwradr:uSnJYwRZ3plpfCuAUwSYhg5FQSAIu7p2wH8FKreJ5FQfolbYH1TcMnvtWnXZB1PKZBmGkATM8wHPiGwRNp2UhA==@kitwradr.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
she_client = pymongo.MongoClient(she_url)
she_db = she_client.LocationData
she_dis = she_db.DisasterData
# def plot(faces,image):
#     plt.figure(figsize=(8, 8))
#     ax = plt.imshow(image, alpha=0.6)
#     for face in faces:
#         fr = face["faceRectangle"]
#         fa = face["faceAttributes"]
#         origin = (fr["left"], fr["top"])
#         p = patches.Rectangle(
#         origin, fr["width"], fr["height"], fill=False, linewidth=2, color='b')
#     ax.axes.add_patch(p)
#     plt.text(origin[0], origin[1], "%s, %d"%(fa["gender"].capitalize(), fa["age"]),
#              fontsize=20, weight="bold", va="bottom")
#     _ = plt.axis("off")
#     plt.show()

#import pdb

app=Flask(__name__)
subscription_key = "22e514c66c98466198feb44d3367b93e"
assert subscription_key

@app.route("/")
def hello():
    return "hello"

@app.route("/weather")
def weather():
    req = requests.get('http://www.imd.gov.in/section/nhac/dynamic/allindiasevere.pdf')
    open_pdf_file =  io.BytesIO(req.content)
    read_pdf = PyPDF2.PdfFileReader(open_pdf_file)
    num_pages = read_pdf.getNumPages()
    res=""
    for i in range(int(num_pages)):
        page_text = read_pdf.getPage(i).extractText()
        splits = page_text.split('\n')
        if i==0:
            res= res+" ".join(splits[5:-8])
        else:
            res= res+" ".join(splits[:-8])
    print(res)
    js={}
    key="rand"
    sentences=res.split('.')
    js[key]=""
    for i in sentences:
        sub_splits=i.split(':')
        if len(sub_splits)>1:
            js[sub_splits[0]] = sub_splits[1]
            key=sub_splits[0]
        else:
            js[key] = js[key] +"."+ sub_splits[0]

    return json.dumps(js)

@app.route('/weather/<city>')
def city_weather(city):
    req = requests.get("http://city.imd.gov.in/citywx/menu.php")
    text = req.text
    cities=[]
    soup = BeautifulSoup(text,'html.parser')
    alink=""
    for link in soup.findAll('a', href=True, target="mainframe"):
        cities.append(link.string)
        if( str(city).lower() in str(link.string).lower()):
            alink = link['href']
    base = "http://city.imd.gov.in/citywx/" + alink
    # print(base)
    # print(cities)
    res={}
    if alink=="":
        res['status']="404"
        res["url"] = base
    else:
        res['status']='200'
        res['url'] = base
    return json.dumps(res)

@app.route("/register",methods=["POST"])
def register():
    reg = request.get_json()
    cursor = db.Master
    cursor.insert_one(reg)
    req = cursor.find_one({"Name":reg["Name"]})
    id_ = str(req["_id"])
    return json.dumps({"status":200,"id":id_})

@app.route("/login",methods=["POST"])
def login_():
    reg = request.get_json
    cursor = db.Master
    req = cursor.find_one({"Name":reg["Name"]})
    
    if req is None or req["Password"] !=reg["Password"]:
        return json.dumps({"status":300,"loggedin":"false","id":""})
    id_ = str(req["_id"])
    return json.dumps({"status":200,"loggedin":"true","id":id_})    


def get_facial(data):
    face_api_url = 'https://southeastasia.api.cognitive.microsoft.com/face/v1.0/detect'

    # Set image_url to the URL of an image that you want to analyze.
    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
    "Content-Type":"application/octet-stream"
    }
    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
        'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
    }
    response = requests.post(face_api_url, params=params, headers=headers, data=data)
    faces = response.json()
    res={}
    # import pdb; pdb.set_trace()
    # plot(faces,data)
    
    # import pdb; pdb.set_trace()

    res["status"] = '200'
    res["num"] = str(len(faces))
    res["ids"] = faces
    return res

@app.route('/victims/<userid>/facial',methods=['POST'])
def facial(userid):
    # import pdb; pdb.set_trace()
    data=bytes(request.get_data())
    res={}
    try:
        res = get_facial(data)
    except:
        res['status'] = '404'
    import pprint
    pprint.pprint(res)
    # import pdb; pdb.set_trace()
    num_males=0
    num_females=0
    num_elders=0
    num_children=0
    faces = res["ids"]
    for i in range(int((res["num"]))):
        if faces[i]['faceAttributes']['gender'].lower() == 'male':
            num_males+=1
        if faces[i]['faceAttributes']['gender'].lower() == 'female':
            num_females+=1
        
        if int(faces[i]['faceAttributes']['age']) > 50:
            num_elders+=1
        if int(faces[i]['faceAttributes']['age']<15):
            num_children+=1

    # print(res)
    if res['status'] !='404':
        cursor = db.Victim
        posts = cursor.find_one({"user_id":userid})

        posts["numvictims"] = res["num"]
        posts["victims"]={"children":num_children,"elders":num_elders,"female":num_females,"males":num_males}
        if posts["issafe"] == "true":
            posts["priority"] = 0
        elif int(res["num"]) <=2:
            posts["priority"] = 0
        elif int(res["num"])>2 and int(res["num"])<=4:
            posts["priority"] = 1
        else:
            posts["priority"] = 2
        cursor.update_one({"user_id":userid},{"$set":posts},upsert=False)
    return json.dumps(res)


@app.route('/rescuer/mapdata',methods=['POST'])
def send():
    '''
    {
        1:{
        "lat":lat,
        longs:long,
        "numstuck":"4",
        "priority":"0-2",
        "children:"2",,
        "female":3
        "elders":"2"
        }

    }
    '''
    
    reqs = db.Victim
    result = reqs.find()
    i=0
    res={}
    df = pd.DataFrame(list(result))
    wdf = df.sample(n=4).reset_index()
    df = df.reset_index()
    users=["1","2","3","4"]
    iters_=0
    base = "https://rvsafeimages.blob.core.windows.net/imagescontainer/"
    for i in range(len(wdf)):
        userid=users[iters_]
        res[userid]={}
        res[userid]["Lat"] = wdf.iloc[i]["Lat"]
        res[userid]["Long"] = wdf.iloc[i]["Long"]
        res[userid]["numstuck"] = str(wdf.iloc[i]["numvictims"])
        res[userid]["priority"] = str(wdf.iloc[i]["priority"])
        res[userid]["female"] = wdf.iloc[i]["victims"]["female"]
        res[userid]["male"] = wdf.iloc[i]["victims"]["males"]
        res[userid]["elders"] = wdf.iloc[i]["victims"]["elders"]
        res[userid]["children"] = wdf.iloc[i]["victims"]["children"]
        res[userid]["user_id"] = str(userid)
        iters_+=1
        li = ['jpeg.jpg','landmark1.jpg','landmark2.jpg','landmark2.jpg','landmark3.jpg','landmark4.jpg','landmark5.jpg','landmark6.jpg','landmark7.jpg','landmark8.jpg']
        li=random.sample(li,3)
        urls=[]
        if len(li)> 3:
            for k in li[len(li)-3:]:
                urls.append(base+k)
        else:
            for k in li:    
                urls.append(base+k)
        res[userid]["blobs"] = urls
    res[df.iloc[0]["user_id"]]={}
    res[df.iloc[0]["user_id"]]["Lat"] = df.iloc[0]["Lat"]
    res[df.iloc[0]["user_id"]]["Long"] = df.iloc[0]["Long"]
    res[df.iloc[0]["user_id"]]["numstuck"] = str(df.iloc[0]["numvictims"])
    res[df.iloc[0]["user_id"]]["priority"] = str(df.iloc[0]["priority"])
    res[df.iloc[0]["user_id"]]["female"] = df.iloc[0]["victims"]["female"]
    res[df.iloc[0]["user_id"]]["male"] = df.iloc[0]["victims"]["males"]
    res[df.iloc[0]["user_id"]]["elders"] = df.iloc[0]["victims"]["elders"]
    res[df.iloc[0]["user_id"]]["children"] = df.iloc[0]["victims"]["children"]
    res[df.iloc[0]["user_id"]]["user_id"] = str(df.iloc[0]["user_id"])
    blobnames = df.iloc[0]["blobnames"]
    li = blobnames[len(blobnames)-3:]
    urls=[]
    if len(li)> 3:
        for k in li[len(li)-3:]:
            urls.append(base+k)
    else:
        for k in li:
            urls.append(base+k)

    res[df.iloc[0]["user_id"]]["blobs"] = urls

    return json.dumps({"status":200,"data":res})




@app.route('/disaster/assets/<params>',methods=['GET'])
def temp(params):
    block_blob_service = BlockBlobService(account_name='rvsafeimages', account_key='391TMmlvDdRWu+AsNX+ZMl1i233YQfP5dxo/xhMrPm22KtwWwwMmM9vFAJpJHrGXyBrTW4OoAInjHnby9Couug==')
    container_name ='imagescontainer'
    #params = params+".jpg"
    block_blob_service.create_container(container_name)
    block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)
    # full_path_to_file2 = os.getcwd()+"/test.jpg"
    # block_blob_service.get_blob_to_path(container_name, params, full_path_to_file2)
    #import pdb; pdb.set_trace()
    data = block_blob_service.get_blob_to_bytes(container_name,params)
    # data = open(full_path_to_file2,"rb").read()
    #import pdb; pdb.set_trace()
    res = Response(data.content,status=200,mimetype="image/jpeg")
    return res

@app.route('/ngo/resources/add',methods=["POST"])
def add():
    '''
        {"userid","","city","phone number","donating items"}
    '''
    import pdb; pdb.set_trace()
    body = request.get_json()
    # import pdb; pdb.set_trace()
    master = db.Master
    curr = master.find_one({"userid":body["id"]})
    body["Name"] = curr["Name"]
    donate = db.resources
    try:
        del body["id"]
    except:
        pass
    donate.insert_one(body)
    return json.dumps({"status":200})


@app.route('/victims/disasters/clusters/<disasterid>',methods=["GET"])
def get_clusters(disasterid):
    
    kms_per_rad = 6371.0088

    # for i in victim_curr:
    #     import pdb; pdb.set_trace()
    #     print(i)
    df = pd.DataFrame(list(db.Victim.find()))

    df = df[df["Disasterid"]==disasterid]
    df["Long"] = df["Long"].astype("float")
    df["Lat"] = df["Lat"].astype("float")
    df["numvictims"] = df["numvictims"].astype("int")

    epsilon = 0.3/kms_per_rad
    safe_victims = df[df["issafe"]=="true"]
    unsafe_victims= df[df["issafe"]=="false"]
    dbsc_unsafe = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(unsafe_victims[['Lat','Long']].as_matrix()))
    dbsc_safe = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(safe_victims[['Lat','Long']].as_matrix()))
    safe_victims["Labels"] = list(dbsc_safe.labels_)
    num_safe = len(dbsc_safe.labels_.tolist())
    unsafe_victims["Labels"] = list(dbsc_unsafe.labels_)
    num_unsafe = len(dbsc_unsafe.labels_.tolist())
    safe_victims =  safe_victims.groupby("Labels").agg({"Lat":"mean","Long":"mean","numvictims":"count"}).reset_index()

    unsafe_victims = unsafe_victims.groupby("Labels").agg({"Lat":"mean","Long":"mean","numvictims":"count"}).reset_index()
    safe_dict = {}
    unsafe_dict={}
    for i in dbsc_safe.labels_:
        lat = safe_victims[safe_victims["Labels"]==i]["Lat"].iloc[0]
        long_ = safe_victims[safe_victims["Labels"]==i]["Long"].iloc[0]
        num_ = safe_victims[safe_victims["Labels"]==i]["numvictims"].iloc[0]
        safe_dict[str(i)]=[lat,long_,int(num_)]
    
    for i in dbsc_unsafe.labels_:
        lat = unsafe_victims[unsafe_victims["Labels"]==i]["Lat"].iloc[0]
        long_ = unsafe_victims[unsafe_victims["Labels"]==i]["Long"].iloc[0]
        num_ = unsafe_victims[unsafe_victims["Labels"]==i]["numvictims"].iloc[0]
        unsafe_dict[str(i)]=[lat,long_,int(num_)]

    res={}
    res["status"]=200
    res["numsafe"] = num_safe
    res["numunsafe"] = num_unsafe
    res["safe"] = safe_dict
    res["unsafe"] = unsafe_dict

    return json.dumps(res)

@app.route('/victims/update', methods=["POST"])
def update_location():
    '''
    {
        'id'
        "user_id is a foreign key
    }
    '''
    req = request.get_json()
    ref = db.Victim
    cursor = ref.find_one({'user_id':req["user_id"]})
    if cursor is None:
        ref.insert_one(req)
    else:
        post = ref.find_one({"user_id":req["user_id"]})
        for attr in req:
            post[attr] = req[attr]
        ref.update_one({"user_id":req["user_id"]},{"$set":post},upsert=False)
    return json.dumps({"status":200})



@app.route('/victim/upload/images/<userid>/<format_>/blob', methods=["POST"])
def upload_images(userid,format_):
    data = request.get_data()
    ref = db.Victim
    cursor = ref.find_one({'user_id':userid})
    if len(list(cursor)) == 0:
        assert("Upload Failed")
    if "num_files" not in cursor:
        cursor["num_files"] = 0
    nums = int(cursor["num_files"]) #nums has to be set to 0.
    nums+=1
    cursor["num_files"] = nums
    if "blobnames" not in cursor:
        files=[]
    else:
        files = cursor["blobnames"]
    uid=userid+str(nums)
    files.append(uid+"."+format_)
    cursor["blobnames"] = files
    ref.update_one({"user_id":userid},{"$set":cursor},upsert=False)
    block_blob_service = BlockBlobService(account_name='rvsafeimages', account_key='391TMmlvDdRWu+AsNX+ZMl1i233YQfP5dxo/xhMrPm22KtwWwwMmM9vFAJpJHrGXyBrTW4OoAInjHnby9Couug==')
    container_name ='imagescontainer'
    block_blob_service.create_blob_from_bytes(container_name,uid+"."+format_,data)
    #save to blob
    return json.dumps({"status":200})
    
    

@app.route('/victim/download/images/<userid>/blob',methods=["POST"])
def download(userid):
    ref = db.Victim
    cursor = ref.find_one({"user_id":userid})
    base_url = "http://aztests.azurewebsites.net/disaster/assets"
    lists=[]
    for i in cursor["blobnames"]:
        lists.append(base_url+'/'+i)
    lists = lists[len(lists)-3:]
    return json.dumps({"status":200,"links":lists})