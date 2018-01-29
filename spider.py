#!/usr/bin/env python2
import re
from six.moves.urllib.parse import urlparse, urljoin, urlsplit, SplitResult
from six.moves.urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
import sys
from scrapme import getProxy
from SiteLibrary import contentScraper, printSiteList, noPrintSiteList, urlValidate, preSeed
from fake_useragent import UserAgent
from time import sleep
import logging
from stdsitelib import hdr

logging.basicConfig(filename = 'spider.log', level = logging.INFO)


def preprocess_url(referrer, url):
    # Clean and filter URLs before scraping.

    if not url:
        return None

    if referrer not in url: #then they are not using absolute links and we need to fix (thanks foodnework.co.uk
        url = startingurl + url

    fields = urlsplit(urljoin(referrer, url))._asdict() # convert to absolute URLs and split
    fields['path'] = re.sub(r'/$', '', fields['path']) # remove trailing /
    fields['fragment'] = '' # remove targets within a page
    fields = SplitResult(**fields)

    if fields.netloc == domain and "replytocom" not in url and "comment" not in url: #the replytocom is because of replies to comments in wp sites
        # Scrape pages of current domain only
        if fields.scheme == 'http':
            httpurl = cleanurl = fields.geturl()
            httpsurl = httpurl.replace('http:', 'https:', 1)
        else:
            httpsurl = cleanurl = fields.geturl()
            httpurl = httpsurl.replace('https:', 'http:', 1)

        if httpurl not in links and httpsurl not in links:
            # Return URL only if it's not already in links
            return cleanurl

    return None

def scrape(url):
    #let's be nice and sleep between attempts
    sleep(2)
    proxy = getProxy()
    #print(proxy)
    print("checking %s" % url)
    response = requests.get(url, headers=hdr, proxies=proxy)
    soup = BeautifulSoup(response.content, 'lxml')
    for link in soup.findAll("a"):
        try:
            childurl = preprocess_url(url, link.get("href").strip()) #foodnetwork.co.uk taught me a lesson on poor href formatting so I have to strip all blank space
            if childurl:
                if childurl not in links:
                    morelinks.add(childurl)
                    doRecipeScrape(childurl)
        except:
            print("error in childurl:%s" % childurl)
            

def explorelinks(morelinks):
    payload = morelinks.copy() #copy to payload to allow for increasing size of morelinks otherwise python chokes :)
    counter = 0 #for testing let's show a counter to know where I am in the queue
    for link in payload:
        scrape(link)
        morelinks.discard(link)  # remove without error from morelinks after scraped or we will search forever
        print("Scraped:%s %s of Payload:%s Morelinks:%s" % (link, counter, len(payload), len(morelinks)))
        counter += 1

def doRecipeScrape(url): #check page for recipes and add to links so we don't search them a second time for a recipe
    if domain in printSiteList:
        if "print" in url:
            #print("Scraping print page {:s} ...".format(url))
            #check if url exists in database
            if url not in links:
                contentScraper(url, domain)
                links.add(url)  # add to links


    if domain in noPrintSiteList and ".rdf" not in url and ".rss" not in url and "print" not in url: #skip news feeds and sites with poorly formated print pages
        #print("Scraping non print page {:s} ...".format(url))
        # check if url exists in database
        if url not in links:
            contentScraper(url, domain)
            links.add(url) #add to links
try:
    #run this thang
    print("%s" % (sys.argv[1])) #for testing
    url = sys.argv[1]

    #### defs
    domain = urlsplit(url).netloc
    startingurl = url

    #get links from database if they exist
    preseed = preSeed(domain)

    #start process
    if len(preseed) > 0: #links come from database meaning they have already been scraped
        links = preseed
    else:
        links = set()
    morelinks = set() #morelinks is anything that's not in the database meaning it's not a recipe
    ######################

    scrape(url) # return links from first page and go from there

    if morelinks:
        while morelinks:
            explorelinks(morelinks)
except IOError as e:
    logging.exception(str(e))
