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
    print(res)
    if re['status'] !='404':
        cursor = db.Victim
        posts = cursor.find_one({"user_id":userid})
        if "numvictims" not in posts:
            posts["numvictims"] = res["num"]
        else:
            posts["numvictims"] += res["num"]
        cursor.update_one({"user_id":userid},{"$set",cursor},upsert=False)
    return json.dumps(res)


@app.route('/victim/location',methods=['POST'])
def location():
    data = request.get_json()
    return json.dumps({"status":200})

@app.route('/victim/mapdata',methods=['POST'])
def send():
    data=request.get_json()
    return json.dumps({"status":200})

@app.route('/rescuer/mapdata',methods=['POST'])
def send_rescuer():
    data = request.get_json()
    return json.dumps({"status":200})


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

@app.route('/ngo/login', methods=['POST'])
def login():
    '''
    data={"'E-mail':xxx,'password':'xxx'"}
    '''
    data = request.get_json()
    ngo = db.ngo_data
    logs = ngo.find_one({"E-mail":data["E-mail"]})
    if logs["Password"] == data["Password"]:
        session["E-mail"] = data["E-mail"]
        return json.dumps({"status":200})
    else:
        return json.dumps({"status":500})


@app.route('/ngo/resources',methods=['GET'])
def resources():
    # if "E-mail" not in session:
    #     return json.dumps({"status":500})
    donate = db.resources
    res=""
    donated = donate.find()
    for cur in donated:
        res+="<tr>"
        for attr in cur:
            if attr == "_id":
                continue
            res+="<td>"+str(cur[attr])+"<td/>"
        res+="<tr/>"

    return json.dumps({"status":200,"data":res})

@app.route('/ngo/resources/add',methods=["POST"])
def add():
    '''
    {"userid","","city","phone number","donating items"}
    '''
    body = request.get_json()
    donate = db.resources
    donate.insert_one(body)
    return json.dumps({"status":200})


@app.route('/victims/diasasters/clusters/<disasterid>',methods=["GET"])
def get_clusters(disasterid):
    
    kms_per_rad = 6371.0088

    victim_curr = db.Victim.find()

    df = pd.DataFrame(list(victim_curr))


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
    import pdb; pdb.set_trace()
    ref = db.Victim
    cursor = ref.find_one({'user_id':req["user_id"]})
    if cursor is None:
        ref.insert_one(req)
    else:
        post = ref.find_one({"user_id":req["user_id"]})
        import pdb; pdb.set_trace()
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
    import pdb; pdb.set_trace()
    if "num_files" not in cursor:
        cursor["num_files"] = 0
    nums = int(cursor["num_files"]) #nums has to be set to 0.
    nums+=1
    cursor["num_files"] = nums
    if "blobnames" not in cursor:
        files=[]
    else:
        files = cursor["blobnames"]
    import pdb; pdb.set_trace()
    uid=userid+str(nums)
    files.append(uid+"."+format_)
    cursor["blobnames"] = files
    ref.update_one({"user_id":userid},{"$set":cursor},upsert=False)
    block_blob_service = BlockBlobService(account_name='rvsafeimages', account_key='391TMmlvDdRWu+AsNX+ZMl1i233YQfP5dxo/xhMrPm22KtwWwwMmM9vFAJpJHrGXyBrTW4OoAInjHnby9Couug==')
    import pdb; pdb.set_trace()
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

    return json.dumps({"status":200,"links":lists})