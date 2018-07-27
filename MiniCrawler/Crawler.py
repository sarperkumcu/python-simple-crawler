import requests
import xml.etree.ElementTree as xml
from time import gmtime, strftime
from multiprocessing import Pool

url = "https://www.mybeautifulwebsite.com/gitsitemap.xml"
logfilePath = strftime("%Y%m%d%H%M%S", gmtime()) + ".log"
log = open(logfilePath, "w") 

class Crawler(requests.Request):

    def __init__(self):
        self.url = ""
        self.sitemaps = []
        self.__result = []
    def resolveSiteMap(self,url):
        root = self.getRoot(url)
        for child in root:
            self.sitemaps.append(child[0].text)
        if(not self.sitemaps):
            self.resolveSiteMap(url)
        else:
            for siteMapUrl in self.sitemaps:
                pool = Pool(processes=2)
                root = self.getRoot(siteMapUrl)
                for child in root:
                    url = child[0].text
                    pool.apply_async(self.crawl,(url,),callback=self.resultCollector)
                pool.close()
                pool.join()
       
    def resultCollector(self,result):
        out = str(result.status_code) + " " + result.reason + "\n" + "Request :" \
                    + result.request.url + "\nResponse: " + result.url + "\n\n"
        print(out)
        if(result.status_code != 200):
            log.write(out)  

    def getRoot(self,url):
        mainXml = requests.get(url)
        tree = xml.ElementTree(xml.fromstring(mainXml.content))
        root = tree.getroot()
        return root

    def crawl(self, url):
        result = requests.head(url,allow_redirects=True)
        return result


def main():
    crawler = Crawler()
    crawler.resolveSiteMap(url)
    log.close()
if __name__ == '__main__':
    main()
