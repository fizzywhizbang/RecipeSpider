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

printSiteList = ['pinchofyum.com','rachlmansfield.com']
noPrintSiteList = ['www.101cookbooks.com']

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
            title = title["content"]
            # link
            link = soup.find('meta', property='og:url')
            link = link["content"]
            # description
            descr = soup.find('meta', property='og:description')
            descr = descr["content"]
            # date
            d = soup.find('meta', property='article:published_time')
            datePosted = d["content"]
            # image link
            img = soup.find('meta', property='og:image')
            img = img["content"]
            # ingredients
            ing = soup.find('div', {'class': 'tasty-recipes-ingredients'})
            ing = ing.get_text()  # remove html entities
            # instructions
            instr = soup.find('div', {'class': 'tasty-recipes-instructions'})
            instr = instr.get_text()
            if ing:
                print("title:%s" % title)  # print title
                #print("Date published %s" % d["content"])
                print("Url: %s" % link)
                print("Description: %s" % descr)
                print(img)  # print image source
                print(ingtxt)  # print ingredients
                print(instr)
                add_recipe = "insert into recipes (title, link, ingredients, description, image , dateposted, instructions) values (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(add_recipe, (title, link , ing, descr, img, instr))
                db.commit()
        except:
            print("no recipe found @ %s" % link)
#all recipes
#incomplete
    if "allrecipes" in url:
        try:
            # title
            title = soup.find('meta', property='og:title')
            title = title["content"]
            # link
            link = soup.find('meta', property='og:url')
            link = link["content"]
            # description
            descr = soup.find('div', {'class': 'recipe-print__description'})
            descr = descr["content"]
            # date
            d = soup.find('meta', itemprop='uploadDate')
            datePosted = d["content"]
            # image link
            img = soup.find('meta', property='og:image')
            img = img["content"]
            # ingredients
            ing = soup.find('div', {'class': 'recpie-print__container2'})
            ing = ing.get_text()  # remove html entities
            # instructions
            instr = soup.find('ol', {'class': 'recipe_print__directions'})
            instr = instr.get_text()
            if ing:
                print("title:%s" % title)  # print title
                print("Date published %s" % datePosted)
                print("Url: %s" % link)
                print("Description: %s" % descr)
                print(img)  # print image source
                print(ing)  # print ingredients
                print(instr)
                add_recipe = "insert into recipes (title, link, ingredients, description, image ,instructions) values (%s, %s, %s, %s, %s, %s)"
                cursor.execute(add_recipe, (title, link, ing, descr, img, instr))
                db.commit()
        except:
            print("no recipe found @ %s" % link)

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
            datePosted = time.strftime('%Y-%m-%d %H:%M:%S')
            # image link
            img = soup.find('link', itemprop='image')
            img = img["href"]
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
                print("Url: %s" % link)
                print("Description: %s" % descr)
                print("imglink: %s" % img)  # print image source
                print("ingredients: %s" % ing)  # print ingredients
                print("instructions: %s" % instr)
                add_recipe = "insert into recipes (title, link, ing, description, image ,dateposted, instructions) values (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(add_recipe, (title, link, ing, descr, img, datePosted, instr))
                db.commit()
        except:
            print("no recipe found @ %s" % link)

#101cookbooks.com
    if "101cookbooks" in url:
        try:
            # title
            title = soup.find('meta', property='og:title')
            title = title["content"]
            #print(title)
            # link
            link = soup.find('meta', property='og:url')
            link = link["content"]
            #print(link)
            # description
            descr = soup.find('meta', {"name":"description"})
            descr = descr["content"]
            #print(descr)
            # date no date
            datePosted = time.strftime('%Y-%m-%d %H:%M:%S')
            # image link
            img = soup.find('meta', property='og:image')
            imglink = img["content"]
            #print(imglink)
            # ingredients
            ingdiv = soup.find('div', id="recipe")
            ing = ""
            #containted in blockquote in recipe div
            for bq in ingdiv.find_all('blockquote'):
                # prints the p tag content
                ing = ing + bq.text + "\n"
            #print(ing)
            # instructions are in the same div as the ingredients but not in the blockquote
            instr = ""
            for p in ingdiv.find_all('p'):
                # prints the p tag content
                instr = instr + p.text + "\n"
            #print(instr)
            if ing:
                print("title:%s" % title)  # print title
                print("Date published %s" % datePosted)
                print("Url: %s" % link)
                print("Description: %s" % descr)
                print("imglink: %s" % imglink)  # print image source
                print("ingredients: %s" % ing)  # print ingredients
                print("instructions: %s" % instr)
                add_recipe = "insert into recipes (title, link, ingredients, description, image ,dateposted, instructions) values (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(add_recipe, (title, link, ing, descr, imglink, datePosted, instr))
                db.commit()

        except:
            print("no recipe found @ %s" % link)