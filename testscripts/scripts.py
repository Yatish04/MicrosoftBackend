from bs4 import BeautifulSoup
import requests
import pdb
import urllib
#req = http.request('GET','http://city.imd.gov.in/citywx/localwx.php')
req = requests.get("http://www.india-water.gov.in/eSWIS-MapViewer/")
text = req.text
pdb.set_trace()
soup = BeautifulSoup(text,'html.parser')
alink=""
for link in soup.findAll('a', href=True, text='Gangtok'):
    alink = link['href']
base = "http://city.imd.gov.in/citywx/" + alink
print(base)
