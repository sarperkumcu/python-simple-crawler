#!/usr/bin/python
import requests
import copy_reg
import types
import xml.etree.ElementTree as xml
from time import gmtime, strftime
from multiprocessing import Pool


url = "https://www.yoursite.com/sitemap/sitemap.xml"
logfilePath = strftime("%Y%m%d%H%M%S", gmtime()) + ".log"
log = open(logfilePath, "w") 

def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

#Crawler start
class Crawler(requests.Request):

    def __init__(self):
         self.url = ""
         self.sitemaps = []
         self.__result = []          

    def resolvesitemap(self, url):
        root = self.getRoot(url)
        for child in root:
            self.sitemaps.append(child[0].text)
        if(not self.sitemaps):
            self.resolvesitemap(url)
        else:                         
            for sitemapurl in self.sitemaps:
                pool = Pool(processes=64)     
                root = self.getRoot(sitemapurl)
                for child in root:
                    url = child[0].text
                    pool.apply_async(self.crawl,(url,), callback=self.resultCollector)
                pool.close()
                pool.join()   

    def resultCollector(self, result):
         out =  str(result.status_code) + " "+ result.reason + "\n" + "Request : " + result.request.url  + "\nResponse : " + result.url + "\n\n" 
         print(out)
         if(result.status_code != 200):
             log.write(out)    

    def getRoot(self,url):
        mainxml = requests.get(url)
        tree = xml.ElementTree(xml.fromstring(mainxml.content))
        root = tree.getroot()
        return root

    def crawl(self, url):
          result = requests.head(url, allow_redirects=True)
          return result

#main
def main():
    crawler = Crawler()
    crawler.resolvesitemap(url)
    log.close()
    pool.close()
if __name__ == '__main__':
    main()
