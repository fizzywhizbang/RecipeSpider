import re
from six.moves.urllib.parse import urlparse, urljoin, urlsplit, SplitResult
from six.moves.urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
import sys
import MySQLdb
import random
from scrapme import getProxy
from fake_useragent import UserAgent
import time
hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


db = MySQLdb.connect(host="localhost", user="root", passwd="helifino", db="recipefinder", charset='utf8', use_unicode=True)
cursor= db.cursor()
proxy = getProxy()

def contentScraper(url):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    response = requests.get(url, headers=hdr, proxies=proxy)
    soup = BeautifulSoup(response.content, "html.parser")
# pinch of yum
    if "pinchofyum" in url:
        try:
            # title
            title = soup.find('meta', property='og:title')
            # link
            link = soup.find('meta', property='og:url')
            # description
            descr = soup.find('meta', property='og:description')
            # date
            d = soup.find('meta', property='article:published_time')
            # image link
            img = soup.find('meta', property='og:image')
            # ingredients
            ing = soup.find('div', {'class': 'tasty-recipes-ingredients'})
            # instructions
            instr = soup.find('div', {'class': 'tasty-recipes-instructions'})

            if ing:
                print("title:%s" % title["content"])  # print title
                title = title["content"]
                #print("Date published %s" % d["content"])
                datePosted = d["content"]
                print("Url: %s" % link["content"])
                link = link["content"]
                print("Description: %s" % descr["content"])
                description = descr["content"]
                print(img["content"])  # print image source
                imglink = img["content"]
                ingtxt = ing.get_text()  # remove html entities
                print(ingtxt)  # print ingredients
                instrtxt = instr.get_text()
                print(instrtxt)
                add_recipe = "insert into recipes (title, link, ingredients, description, image , dateposted, instructions) values (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(add_recipe, (title, link , ingtxt, description, imglink, instrtxt))
                db.commit()
        except:
            #if fail log
            add_log = "insert into faillog (link,timestamp) values (%s, %s)"
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(add_log, url, ts)
#all recipes
#incomplete
    if "allrecipes" in url:
        try:
            # title
            title = soup.find('meta', property='og:title')
            # link
            link = soup.find('meta', property='og:url')
            # description
            descr = soup.find('div', {'class': 'recipe-print__description'})
            # date
            d = soup.find('meta', itemprop='uploadDate')
            # image link
            img = soup.find('meta', property='og:image')
            # ingredients
            ing = soup.find('div', {'class': 'recpie-print__container2'})
            # instructions
            instr = soup.find('ol', {'class': 'recipe_print__directions'})

            if ing:
                print("title:%s" % title["content"])  # print title
                title = title["content"]
                print("Date published %s" % d["content"])
                datePosted = d["content"]
                print("Url: %s" % link["content"])
                link = link["content"]
                print("Description: %s" % descr["content"])
                description = descr["content"]
                print(img["content"])  # print image source
                imglink = img["content"]
                ingtxt = ing.get_text()  # remove html entities
                print(ingtxt)  # print ingredients
                instrtxt = instr.get_text()
                print(instrtxt)
                add_recipe = "insert into recipes (title, link, ingredients, description, image ,instructions) values (%s, %s, %s, %s, %s, %s)"
                cursor.execute(add_recipe, (title, link, ingtxt, description, imglink, instrtxt))
                db.commit()
        except:
            # if fail log
            add_log = "insert into faillog (link,timestamp) values (%s, %s)"
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(add_log, url, ts)
#rachelmansfield
    if "rachlmansfield" in url:
        try:
            # title
            title = soup.find('div', itemprop='name')
            title = title.get_text()
            #print(title)
            # link
            link = soup.find('div', {'class': 'ERPTagline'})
            linktxt = link.get_text()
            linktxt = linktxt.replace("rachLmansfield","")
            linktxt = linktxt.replace("Recipe by","")
            linktxt = linktxt.replace("at","")
            link = linktxt.strip()
            #print(link)
            # description contains no description on print page so we'll use the title which is pretty descriptive
            descr = title
            # date no date
            #d = soup.find('meta', itemprop='uploadDate')
            datePosted = time.strftime('%Y-%m-%d %H:%M:%S')
            # image link
            img = soup.find('link', itemprop='image')
            #print(img["href"])
            # ingredients
            ingdiv = soup.find('div', {'class': 'ERSIngredients'})
            ing = ""
            for litag in ingdiv.find_all('li', class_='ingredient'):
                # prints the p tag content
                ing=ing + litag.text + "\n"
            #print(ing)
            # instructions
            instrdiv = soup.find('div', {'class': 'ERSInstructions'})
            instr = ""
            for litag in instrdiv.find_all('li', class_='instruction'):
                # prints the p tag content
                instr = instr + litag.text + "\n"

            if ing:
                print("title:%s" % title)  # print title
                print("Date published %s" % datePosted)

                link = link
                print("Url: %s" % link)
                description = descr
                print("Description: %s" % description)
                imglink = img["href"]
                print("imglink: %s" % imglink)  # print image source
                ingtxt = ing  # remove html entities
                print("ingredients: %s" % ingtxt)  # print ingredients
                instrtxt = instr
                print("instructions: %s" % instrtxt)
                add_recipe = "insert into recipes (title, link, ingredients, description, image ,dateposted, instructions) values (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(add_recipe, (title, link, ingtxt, description, imglink, datePosted, instrtxt))
                db.commit()
        except:
            #if fail log
            add_log = "insert into faillog (link,timestamp) values (%s, %s)"
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(add_log, url, ts)