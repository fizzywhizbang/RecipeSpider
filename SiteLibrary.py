def contentScraper(self, url):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    req = Request(url, headers=headers, proxy=proxies)

    html = urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
# pinch of yum
    if "pinchofyum" in url:
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
            cursor.execute(add_recipe, (title, link , ingtxt, description, imglink, instrtxt))
            db.commit()
#all recipes
#incomplete
    if "allrecipes" in url:
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