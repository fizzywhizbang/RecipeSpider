import requests
import sys
from scrapme import getProxy
from PIL import Image
from StringIO import StringIO
from resizeimage import resizeimage

#define header for request to look like a browser
hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

#get a proxy so I don't get blocked from spidering web sites (it has happened already)
proxy = getProxy()

def imagegrabber(url):
    data = requests.get(url, headers=hdr, proxies=proxy)
    image = Image.open(StringIO(data.content))

    if image.size[1] > 400:
        img = resizeimage.resize_height(image, 400)
        result = StringIO()
        format = "JPEG"
        img.save(result, format)
        image = result.getvalue()
    else:
        image = data.content

    return image