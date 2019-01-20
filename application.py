#import urllib3
from bs4 import BeautifulSoup
from bson import ObjectId   
import requests,PyPDF2, io
from sklearn.cluster import DBSCAN
import numpy as np
import fitz
import pandas as pd
#import pdb
from flask import *
from azure.storage.blob import BlockBlobService, PublicAccess
import json
import time
# import matplotlib.pyplot as plt
# from PIL import Image
# from matplotlib import patches
from ast import literal_eval
from io import BytesIO
import cognitive_face as cf
import random
import pymongo
import os
uri = "mongodb://yatishhr:skv5d9yiRMuHeS0ft5aYipjLAErgy0KEg5iacaWTWUW5JwdskJAlXVYZagWJfWD46ZILskdyxDWhtH2YXl7YdA==@yatishhr.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"

# uri = "mongodb://yatishhr:pXYRVwZL2myXglrdgLSwAVKUb5U8AnbN1m83JXogbpKXlmwBBOdk4Py6s7EgBGsJoWRvTFJ6o7nNDY1n99HHMw==@yatishhr.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
client = pymongo.MongoClient(uri)
db = client.Azure

#RescueGroupData
#latitude
#longitude

she_url = "mongodb://hackathon1:WDe06PPSkGeGaGfEs0MB11nRSvAadFTPNkhToqU0vAsMwvSpbYUs2qxzBQu6LznPk23y56ZLBBwSZ5iiwonn7g==@hackathon1.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"
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
subscription_key = "501f22c3797048d2a73ae58a83ea9069"
assert subscription_key




from fpdf import FPDF

title = 'RVSAFE Medical Report'

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(0, 80, 180)
        # self.set_fill_color(230, 230, 0)
        # self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, '%s' % (label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name):
        # Read text file
        txt="This is a sample txt"
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, num, json1, name):
        self.add_page()
        for i in json1:

            self.chapter_title(num, i.title()+" : "+ json1[i].title())








@app.route("/")
def hello():
    return "hello"

@app.route("/weather")
def weather():
    req = requests.get('http://www.imd.gov.in/section/nhac/dynamic/allindiasevere.pdf')
    doc = fitz.open("pdf",req.content)
    num_pages = doc.pageCount
    res=""
    for i in range(int(num_pages)):
        page_text = doc.getPageText(i)
        splits = page_text.split('\n')
        if i==0:
            res= res+" ".join(splits[5:-5])
            try:
                temp = res.split('♦')
                res = ''.join(temp)
            except:
                pass
        else:
            res= res+" ".join(splits[:-5])
            try:
                temp = res.split('♦')
                res = ''.join(temp)
            except:
                pass


    # print(res)
    js={}
    key="rand"
    sentences=res.split('.')
    js[key]=""
    for i in sentences:
        sub_splits=i.split(':')
        if len(sub_splits)>1:
            js[sub_splits[0]] = sub_splits[1][2:]
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
    face_api_url = 'https://australiaeast.api.cognitive.microsoft.com/face/v1.0/detect'

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


def addfacial(data,user_id,format_):
    ref = db.Victim
    cursor = ref.find_one({'user_id':user_id})
    if len(list(cursor)) == 0:
        assert("Upload Failed")
    
    uid=user_id+"facial"
    cursor["facial"] = "https://rvsafeimages.blob.core.windows.net/imagescontainer/"+uid+'.'+format_
    ref.update_one({"user_id":user_id,"Disasterid":str(cursor["Disasterid"])},{"$set":cursor},upsert=False)
    block_blob_service = BlockBlobService(account_name='rvsafeimages', account_key='391TMmlvDdRWu+AsNX+ZMl1i233YQfP5dxo/xhMrPm22KtwWwwMmM9vFAJpJHrGXyBrTW4OoAInjHnby9Couug==')
    container_name ='imagescontainer'
    block_blob_service.create_blob_from_bytes(container_name,uid+"."+format_,data)
    #save to blob

    


@app.route('/victims/<userid>/facial',methods=['POST'])
def facial(userid):
    # import pdb; pdb.set_trace()
    data=bytes(request.get_data())
    res={}
    addfacial(data,userid,"jpg")
    try:
        res = get_facial(data)
    except:
        res['status'] = '404'
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
        cursor.update_one({"user_id":userid,"Disasterid":posts["Disasterid"]},{"$set":posts},upsert=False)
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
    wdf = df.sample(n=3).reset_index()
    df = df.reset_index()
    users=["1","2","3","4"]
    iter_images=0
    iters_=0
    li = ['landmark1.jpg','landmark2.jpg','landmark3.jpg','landmark4.jpg','landmark5.jpg','landmark6.jpg','landmark7.jpg','landmark8.jpg','landmark9.jpg',"jpeg.jpg"]
    base = "https://rvsafeimages.blob.core.windows.net/imagescontainer/"
    for i in range(len(wdf)):
        userid=users[iters_]
        res[userid]={}
        res[userid]["Lat"] = wdf.iloc[i]["Lat"]
        res[userid]["Long"] = wdf.iloc[i]["Long"]
        res[userid]["numstuck"] = str(wdf.iloc[i]["numvictims"])
        res[userid]["priority"] = str(wdf.iloc[i]["priority"])
        temp_dict = literal_eval(wdf.iloc[i]["victims"])
        res[userid]["female"] = temp_dict["female"]
        res[userid]["male"] = temp_dict["males"]
        res[userid]["elders"] = temp_dict["elders"]
        res[userid]["children"] = temp_dict["children"]
        res[userid]["user_id"] = str(userid)
        iters_+=1
        
        urls=[]

        for nums in range(0,3):
            k = li[iter_images]
            iter_images+=1
            urls.append(base+k)


  
        res[userid]["blobs"] = urls
    res[df.iloc[0]["user_id"]]={}
    res[df.iloc[0]["user_id"]]["Lat"] = df.iloc[0]["Lat"]
    res[df.iloc[0]["user_id"]]["Long"] = df.iloc[0]["Long"]
    res[df.iloc[0]["user_id"]]["numstuck"] = str(df.iloc[0]["numvictims"])
    res[df.iloc[0]["user_id"]]["priority"] = str(df.iloc[0]["priority"])
    try:
        temp_dict = literal_eval(df.iloc[0]["victims"])
    except:
        temp_dict = df.iloc[0]["victims"]
    res[df.iloc[0]["user_id"]]["female"] = temp_dict["female"]
    res[df.iloc[0]["user_id"]]["male"] = temp_dict["males"]
    res[df.iloc[0]["user_id"]]["elders"] = temp_dict["elders"]
    res[df.iloc[0]["user_id"]]["children"] = temp_dict["children"]
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
    # import pdb; pdb.set_trace()
    body = request.get_json()
    # import pdb; pdb.set_trace()
    # master = db.Master
    # curr = master.find_one({"userid":body["id"]})
    body["Name"] = "Shubham"
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


def update_nearest(latitude,longitude):
    ref = she_db.RescueGroupData.find_one({"_id":1})
    df = pd.DataFrame(list(db.Victim.find()))
    df = df[df["issafe"]=="true"]
    # import pdb; pdb.set_trace()
    df["Lat"] = df["Lat"].astype("float")
    df["Long"] = df["Long"].astype("float")
    df["mins"] = (df["Lat"]-float(latitude))**2+(df["Long"]-float(longitude))**2
    min_ = min(i for i in df["mins"] if i > 0)
    series = df[df["mins"]==min_]
    ref["latitude"] = series.iloc[0]["Lat"]
    ref["longitude"] = series.iloc[0]["Long"]
    # ref["longitude"] = 77.4891
    # ref["latitude"] = 12.9223
    she_db.RescueGroupData.update_one({"_id":1},{"$set":ref},upsert=False)




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
    update_nearest(req["Lat"],req["Long"])

    if cursor is None:
        ref.insert_one(req)
    else:
        post = ref.find_one({"user_id":req["user_id"]})
        for attr in req:
            post[attr] = req[attr]
        ref.update_one({"user_id":req["user_id"],"Disasterid":post["Disasterid"]},{"$set":post},upsert=False)
    return json.dumps({"status":200})



@app.route('/victim/upload/images/<userid>/<disasterid>/<format_>/blob', methods=["POST"])
def upload_images(userid,disasterid,format_):
    data = request.get_data()
    ref = db.Victim
    # import pdb; pdb.set_trace()
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

    try:
        files = literal_eval(files)
    except:
        pass

    uid=userid+str(nums)
    files.append(uid+"."+format_)
    cursor["blobnames"] = files
    ref.update_one({"user_id":userid,"Disasterid":disasterid},{"$set":cursor},upsert=False)
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

@app.route('/download', methods=["GET"])
def download_app():
    # import pdb; pdb.set_trace()
    import os
    return send_file(os.getcwd()+'/RVSAFE.apk',as_attachment=True,attachment_filename='RVSAFE.apk')

@app.route('/download/server',methods=["GET"])
def download_server():
    import os
    return send_file(os.getcwd()+'/InstaHelp.apk',as_attachment=True,attachment_filename='InstaHelp.apk')

@app.route('/victims/update/medical',methods=['POST'])
def update_medical():
    js=request.get_json()
    user_id=js["user_id"]
    blood=js['blood']
    height=js['height']
    weight=js['weight']
    cond=js["medical_condition"]
    allergy=js["allergy"]
    notes=js["notes"]
    name=js["name"]
    we=db.Victim.find_one({"user_id":user_id})
    if "medical" in we and "blob" in we["medical"]:
        b=we["medical"]["blob"]
        we["medical"]={"name":name,"blood":blood,"height":height,"weight":weight,"medical_condition":cond,"allergy":allergy,"notes":notes,"blob":b}
    else:
        we["medical"]={"name":name,"blood":blood,"height":height,"weight":weight,"medical_condition":cond,"allergy":allergy,"notes":notes}
    
    db.Victim.update_one({"user_id":user_id,"_id":we["_id"]},{"$set":we},upsert=False)
    return json.dumps({"status":200})

@app.route('/victims/upload/<user_id>/<format_>/medical',methods=["POST"])
def upload_medical_records(format_,user_id):
    data = request.get_data()
    block_blob_service = BlockBlobService(account_name='rvsafeimages', account_key='391TMmlvDdRWu+AsNX+ZMl1i233YQfP5dxo/xhMrPm22KtwWwwMmM9vFAJpJHrGXyBrTW4OoAInjHnby9Couug==')
    container_name ='imagescontainer'
    
    block_blob_service.create_blob_from_bytes(container_name,"medical"+str(user_id)+"."+format_,data)
    we=db.Victim.find_one({"user_id":user_id})
    we["medical"]["blob"] = "https://rvsafeimages.blob.core.windows.net/imagescontainer/"+"medical"+str(user_id)+"."+format_
    db.Victim.update_one({"user_id":user_id,"_id":we["_id"]},{"$set":we},upsert=False)
    return json.dumps({"staus":200})

@app.route('/victims/get/<user_id>/medical',methods=["GET"])
def get_medical(user_id):
    cur=db.Victim.find_one({"user_id":user_id})
    pdf = PDF()
    pdf.set_title(title)
    pdf.set_author('RVSAFE')
    pdf.print_chapter(1, cur['medical'], '20k_c1.txt')
    pdf.output(user_id+'.pdf', 'F')
    
    return send_file(os.getcwd()+'/'+user_id+'.pdf',as_attachment=True,attachment_filename=user_id+'.pdf')
     


@app.route('/flushandcreate')
def flush():
    PERSON_GROUP_ID = 'victims'
    BASE_URL='https://australiaeast.api.cognitive.microsoft.com/face/v1.0'
    cf.BaseUrl.set(BASE_URL)
    cf.Key.set(subscription_key)
    try:
        # cf.large_person_group.create('v')
        cf.person_group.delete('victims')
    except:
        print('couldnt delete')
        pass
    
    try:
        cf.person_group.create('victims')
    except:
        print('couldnt create')
        pass
    return json.dumps({'status':200})

@app.route('/victims/group/create/faceid',methods=['POST'])
def create_faceid():
    js=request.get_json()
    name=js['name']
    BASE_URL='https://australiaeast.api.cognitive.microsoft.com/face/v1.0'
    cf.BaseUrl.set(BASE_URL)
    cf.Key.set(subscription_key)
    PERSON_GROUP_ID = 'victims' 
    response = cf.person.create(PERSON_GROUP_ID, name)
    return json.dumps(response)


def train():
    PERSON_GROUP_ID='victims'
    


@app.route('/victims/group/<faceid>/addface',methods=['POST'])
def add_faces(faceid):
    data = request.get_data()
    PERSON_GROUP_ID = 'victims'
    face_api_url = 'https://australiaeast.api.cognitive.microsoft.com/face/v1.0/persongroups/{}/persons/{}/persistedFaces'.format(PERSON_GROUP_ID,faceid)
    headers={}
    headers['Content-Type']= 'application/octet-stream'
    headers['Ocp-Apim-Subscription-Key'] = subscription_key
    response=requests.post(url=face_api_url,data=data,headers=headers)
    print(response.text)
    BASE_URL='https://australiaeast.api.cognitive.microsoft.com/face/v1.0'
    cf.BaseUrl.set(BASE_URL)
    cf.Key.set(subscription_key)
    cf.person_group.train(PERSON_GROUP_ID)
    print(cf.person_group.get_status(PERSON_GROUP_ID))
    return json.dumps({"status":"200"})


@app.route('/victims/is_safe',methods=['POST'])
def safevictims():
    js=request.get_json()
    d=db.ngo_data.find_one({'intent':'safe'})
    for i in d['rescued']:
        if js['name'] in i[0]:
            return json.dumps({'status':200,"message":"found","url":i[1]})
    return json.dumps({'status':400,'message':'notfound'})


def getname(personid):
    d=db.ngo_data.find_one({'type':'safe'})
    PERSON_GROUP_ID='victims'
    personlist=cf.person.lists(PERSON_GROUP_ID)
    for i in d["rescued_urls"]:
        response = cf.face.detect(i)
        face_ids = [d['faceId'] for d in response]
        identified_faces = cf.face.identify(face_ids, PERSON_GROUP_ID)
        for k in identified_faces:
            for j in personlist:
                try:
                    for t in k['candidates']:
                        if 'personId' in t:
                            if t['personId']==j['personId']==personid: 
                                return (i,j['name'])
                except:
                    pass


    return "",""


@app.route('/victims/group/dummy/<seq>/<faceid>/addface',methods=['POST'])
def add_faces1(faceid,seq):
    data = request.get_data()
    PERSON_GROUP_ID = 'victims'
    face_api_url = 'https://australiaeast.api.cognitive.microsoft.com/face/v1.0/persongroups/{}/persons/{}/persistedFaces'.format(PERSON_GROUP_ID,faceid)
    headers={}
    headers['Content-Type']= 'application/octet-stream'
    headers['Ocp-Apim-Subscription-Key'] = subscription_key
    response=requests.post(url=face_api_url,data=data,headers=headers)
    print(response.text)
    BASE_URL='https://australiaeast.api.cognitive.microsoft.com/face/v1.0'
    cf.BaseUrl.set(BASE_URL)
    cf.Key.set(subscription_key)
    cf.person_group.train(PERSON_GROUP_ID)
    print(cf.person_group.get_status(PERSON_GROUP_ID))
    time.sleep(2)
    loc="reliefcamp0"
    if seq=='9':
        url,name=getname(faceid)
        if len(url)==0:
            loc=""
        return json.dumps({"status":200,"url":url,"name":name,"loc":loc})
    return json.dumps({"status":"200"})