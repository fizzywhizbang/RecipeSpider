#!/usr/bin/env python2
import re
from six.moves.urllib.parse import urlparse, urljoin, urlsplit, SplitResult
from six.moves.urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
import sys
import MySQLdb
import random
from scrapme import getProxy
from SiteLibrary import contentScraper
from fake_useragent import UserAgent
from time import sleep

hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


db = MySQLdb.connect(host="localhost", user="root", passwd="helifino", db="recipefinder", charset='utf8', use_unicode=True)
cursor= db.cursor()

class RecursiveScraper:
    ''' Scrape URLs in a recursive manner.
    '''
    def __init__(self, url):
        ''' Constructor to initialize domain name and main URL.
        '''
        self.domain = urlsplit(url).netloc
        self.mainurl = url
        self.urls = set()

    def preprocess_url(self, referrer, url):
        ''' Clean and filter URLs before scraping.
        '''
        if not url:
            return None

        fields = urlsplit(urljoin(referrer, url))._asdict() # convert to absolute URLs and split
        fields['path'] = re.sub(r'/$', '', fields['path']) # remove trailing /
        fields['fragment'] = '' # remove targets within a page
        fields = SplitResult(**fields)
        if fields.netloc == self.domain:
            # Scrape pages of current domain only
            if fields.scheme == 'http':
                httpurl = cleanurl = fields.geturl()
                httpsurl = httpurl.replace('http:', 'https:', 1)
            else:
                httpsurl = cleanurl = fields.geturl()
                httpurl = httpsurl.replace('https:', 'http:', 1)
            if httpurl not in self.urls and httpsurl not in self.urls:
                # Return URL only if it's not already in list
                #print(cleanurl)
                return cleanurl

        return None
    def urlValidate(self,url=None):
        query="select * from recipes where link=%s"
        cursor.execute(query, [url])
        result = cursor.fetchone()
        return result

    def scrape(self, url=None):
        ''' Scrape the URL and its outward links in a depth-first order.
            If URL argument is None, start from main page.
        '''
        if url is None:
            url = self.mainurl
        #check if url exists in database
        print("Scraping {:s} ...".format(url))
        if "print" in url:

            if self.urlValidate(url) == 0:
                contentScraper(url)
            else:
                print("%s exists" % url)

        self.urls.add(url)

        #let's be nice and sleep between attempts
        sleep(1)
        proxy = getProxy()
        print(proxy)

        response = requests.get(url, headers=hdr, proxies=proxy)
        soup = BeautifulSoup(response.content, 'lxml')
        for link in soup.findAll("a"):
            childurl = self.preprocess_url(url, link.get("href"))
            if childurl:
                self.scrape(childurl)


if __name__ == '__main__':
    print("%s" % (sys.argv[1])) #for testing
    #instantiate recursive scraper with domain supplied at the command line
    rscraper = RecursiveScraper(sys.argv[1])
    #rscraper = RecursiveScraper("https://pinchofyum.com/recipes/")
    #scrape the url
    rscraper.scrape()
    #print the urls
    #print(rscraper.urls)

db.close()
