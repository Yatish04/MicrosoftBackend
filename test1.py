import requests

data = open('16x9.jpeg','rb').read()
import pdb; pdb.set_trace()
res = requests.post(url='http://127.0.0.1:8080/victims/0/facial',
                    data=data,
                    headers={'Content-Type': 'application/octet-stream'})
#data = requests.get('http://127.0.0.1:8080/disaster/jpeg.jpg')
import pdb; pdb.set_trace()
