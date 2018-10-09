import requests

data = open('jpeg.jpg','rb').read()
import pdb; pdb.set_trace()
res = requests.post(url='http://aztests.azurewebsites.net/facial',
                    data=data,
                    headers={'Content-Type': 'application/octet-stream'})
#data = requests.get('http://127.0.0.1:8080/disaster/jpeg.jpg')
import pdb; pdb.set_trace()
