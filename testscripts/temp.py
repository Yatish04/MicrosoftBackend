import requests
import PyPDF2,io
import pdb

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

    print(js)

weather()
