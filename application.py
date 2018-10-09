#import urllib3
from bs4 import BeautifulSoup
import requests,PyPDF2, io
#import pdb
from flask import *
from azure.storage.blob import BlockBlobService, PublicAccess
import json
# import matplotlib.pyplot as plt
# from PIL import Image
# from matplotlib import patches
from io import BytesIO

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

@app.route('/facial',methods=['POST'])
def facial():
    # import pdb; pdb.set_trace()
    data=bytes(request.get_data())
    res={}
    try:
        res = get_facial(data)
    except:
        res['status'] = '404'
    print(res)
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


@app.route('/disaster/<params>',methods=['GET'])
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
