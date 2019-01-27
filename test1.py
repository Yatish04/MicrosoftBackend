import requests

data = open('1.jpeg','rb').read()
import pdb; pdb.set_trace()
subscription_key="501f22c3797048d2a73ae58a83ea9069"

res = requests.post(url="http://aztests.azurewebsites.net/victims/group/dummy/9/676e67b4-a094-4ae8-9c69-e235724c2b56/addface",data=data,headers={'Content-Type': 'application/octet-stream'})
#data = requests.get('http://127.0.0.1:8080/disaster/jpeg.jpg')
import pdb; pdb.set_trace()

