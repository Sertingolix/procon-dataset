import scrapy
import os
from bs4 import BeautifulSoup
import re
import urllib.parse

class ArgumentSpider(scrapy.Spider):
    name = "argument"

    #define urls where spyder starts searching from
    start_urls = [
            'https://www.procon.org/'
        ]
        
    def parse(self, response):

        #fix broken html and create soup
        soup = BeautifulSoup(response.body, 'lxml')
        text = soup.prettify()
        soup = BeautifulSoup(text, 'lxml')

        #save file
        filename = response.url.replace('/','')+'.html'
        path = os.path.abspath('./intermediate_data/html/')
        with open(path+'/'+filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        # find all links on page
        links=[]
        for link in soup.find_all('a'):
            #print(link)
            links.append(link.get('href'))

        #follow links we want to crawl or have other overview
        links = self.link_process(links, response.url)

        #crawl all links
        for a in links:
            yield response.follow(a, callback=self.parse)

    
    def link_process(self, links, response_url):
        #parse all links
        for i in range(len(links)):
            if links[i]==None:
                links[i]='/'
            if not 'http' in links[i]:
                links[i] = urllib.parse.urljoin(response_url, links[i])

        #only keep links we want
        good_links = []
        for link in links:
            if self.eval_link(link):
                good_links.append(link)
        return good_links

    def eval_link(self, link):
        #prevent crawling facebook sites
        if 'facebook.com' in link:
            return False

        if not 'procon.org' in link:
            return False
            
        #links we allway take
        if 'procon.org/headline.php?headlineID' in link:
            return True
        if 'procon.org/view.answers.php?questionID' in link:
            return True
        
        #left to get links from subdomain but not www.procon.org
        if 'www.procon.org' in link:
            return False
        if '.procon.org' in link:
            #make sure nothing folows after
            split = link.split('.procon.org',1)
            if len(split[1])>1:#'/' is allowed
                return False
            #no reader-comment
            if 'reader-comments.php' in link:
                return False
            return True
        return False