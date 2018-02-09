#!/usr/bin/env python2
import re
from six.moves.urllib.parse import urljoin, urlsplit, SplitResult
import requests
from bs4 import BeautifulSoup
import sys
from SiteLibrary import contentScraper, printSiteList, noPrintSiteList, preSeed, getProxy, urlValidate, linktempAdd, checkTemp, dumpLinksTemp
from time import sleep
import logging
import os
import signal
import psutil

logging.basicConfig(filename='spider.log', level=logging.INFO)

hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

def getMem():
    ram = psutil.virtual_memory()
    ram_total = ram.total / 2 ** 20  # MiB.
    ram_used = ram.used / 2 ** 20
    ram_free = ram.free / 2 ** 20
    ram_percent_used = ram.percent
    return ram_percent_used

def killproc(pid):
    os.kill(pid, signal.SIGTERM)

def preprocess_url(referrer, url):
    ''' Clean and filter URLs before scraping.
    '''
    if not url:
        return None

    fields = urlsplit(urljoin(referrer, url))._asdict()  # convert to absolute URLs and split
    fields['path'] = re.sub(r'/$', '', fields['path'])  # remove trailing /
    fields['fragment'] = ''  # remove targets within a page
    fields = SplitResult(**fields)

    if fields.netloc == domain and "replytocom" not in url and "comment" not in url:  # the replytocom is because of replies to comments in wp sites
        # Scrape pages of current domain only
        if fields.scheme == 'http':
            httpurl = cleanurl = fields.geturl()
            httpsurl = httpurl.replace('http:', 'https:', 1)
        else:
            httpsurl = cleanurl = fields.geturl()
            httpurl = httpsurl.replace('https:', 'http:', 1)
        if constrain in httpsurl or constrain in httpurl:
            return cleanurl

    return None


def scrape(url):
    # let's be nice and sleep between attempts
    sleep(2)
    proxy = getProxy()
    # print(proxy)
    print("checking %s" % url)
    response = requests.get(url, headers=hdr, proxies=proxy)
    soup = BeautifulSoup(response.content, 'lxml')
    for link in soup.findAll("a"):
        childurl = preprocess_url(url, link.get("href"))
        if type(childurl) is str:  # if this is a string then clean the url
            childurl = childurl.strip()  # thanks for the lesson on poorly formated code from foodnetwork.co.uk

        if childurl:
            if checkTemp(childurl) == 0:
                morelinks.add(childurl)
                if childurl not in startingurl:
                    linktempAdd(childurl)
                print("checking %s for recipe" % childurl)
                doRecipeScrape(childurl)

def explorelinks(morelinks):
    payload = morelinks.copy()  # copy to payload to allow for increasing size of morelinks otherwise python chokes :)
    counter = 0  # for testing let's show a counter to know where I am in the queue
    for link in payload:
        print(link)
        scrape(link)
        morelinks.discard(link)  # remove without error from morelinks after scraped or we will search forever
        print("Scraped:%s %s of Payload:%s Morelinks:%s" % (link, counter, len(payload), len(morelinks)))
        counter += 1
        if len(morelinks) == 0:
            dumpLinksTemp()
            break


def doRecipeScrape(url):  # check page for recipes and add to links so we don't search them a second time for a recipe
    memoryUse = getMem()
    print("#################################")
    print("utilization: %.2f%%" % memoryUse)

    if domain in printSiteList:
        if "print" in url:
            # check if url exists in database
            if urlValidate(url) == 0:
                contentScraper(url, domain)
    if domain in noPrintSiteList and ".rdf" not in url and ".rss" not in url and "print" not in url and "replyto" not in url:  # skip news feeds and sites with poorly formated print pages
        # check if url exists in database
        if urlValidate(url) == 0:
            contentScraper(url, domain)

    if memoryUse >= 85: #let's kill the process if utilization gets dangerously high
        #dump more links to file to pickup where we left off since I don't have the ram to run this and may never
        filename = domain + ".txt"
        f = open(filename,"w")
        print(len(morelinks))
        for item in morelinks:
            f.write(item + "\n")
            print(item)
        f.close()
        dumpLinksTemp()
        killproc(process)
        return False

try:
    # run this thang
    print("%s" % (sys.argv[1]))  # for testing
    url = sys.argv[1]

    #### defs
    domain = urlsplit(url).netloc
    startingurl = url
    if len(sys.argv) > 2:
        constrain = url + sys.argv[2]
    else:
        constrain = ""

    #dump temp links just in case the program didn't close nicely
    dumpLinksTemp()

    #get my process id
    process = filter(lambda p: p.name() == "python2" and p.username() == "marc", psutil.process_iter())
    for i in process:
        process = i.pid
        print("Process ID:%s" % process)

    # start process
    morelinks = set()  # morelinks is anything that's not in the database meaning it's not a recipe
    ######################

    scrape(url)  # return links from first page and go from there
    if morelinks:
        while morelinks:
            explorelinks(morelinks)

    #dumpLinksTemp()  # temp temp table contents

except IOError as e:
    logging.exception(str(e))