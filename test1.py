import requests

data = open('gp3.jpeg','rb').read()
import pdb; pdb.set_trace()
subscription_key="501f22c3797048d2a73ae58a83ea9069"

res = requests.post(url="http://127.0.0.1:8080/victims/group/dummy/9/d5986c90-64f3-4ced-aa25-76265cc92b12/addface",data=data,headers={'Content-Type': 'application/octet-stream'})
#data = requests.get('http://127.0.0.1:8080/disaster/jpeg.jpg')
import pdb; pdb.set_trace()

