import requests
from PIL import Image
from StringIO import StringIO
from resizeimage import resizeimage
from six.moves.urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
from time import sleep

#define header for request to look like a browser
hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

#get a proxy so I don't get blocked from spidering web sites (it has happened already)
def imagegrabber(url):
    proxy = getProxy()
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


ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]

# Main function
def getProxy():
    # Retrieve latest proxies
    try:
        proxies_req = Request('https://www.sslproxies.org/')
        proxies_req.add_header('User-Agent', ua.random)
        proxies_doc = urlopen(proxies_req).read().decode('utf8')

        soup = BeautifulSoup(proxies_doc, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')

        # Save proxies in the array
        for row in proxies_table.tbody.find_all('tr'):
            proxies.append({
                'ip':   row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })

        # Choose a random proxy
        proxy_index = random_proxy()
        proxy = proxies[proxy_index]

        proxy_index = random_proxy()
        proxy = proxies[proxy_index]
        return proxy
    except:
        #slow down proxy requests
        sleep(2)
        getProxy()


# Retrieve a random index proxy (we need the index to delete it if not working)
def random_proxy():
  return random.randint(0, len(proxies) - 1)