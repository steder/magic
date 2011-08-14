import os
import time
import urllib

import html5lib
from html5lib import treebuilders

from twisted.web import client
from twisted.internet import defer
from twisted.internet import reactor

setNames = open("sets.txt","r").readlines()
setNames = [n.replace("\r\n","") for n in setNames]
setNames = [urllib.quote("\""+n+"\"") for n in setNames]



class GatherSearchResultsDownloader(object):
    def __init__(self, setName):
        self.PAGE_NUMBER = 0
        self.filename = urllib.unquote(setName).replace("\"", "")
        self.FILENAME_PATTERN = os.path.join("html", self.filename + "_page%s.html")
        self.ERROR_CODE = 400
        self.NPAGES = 1
        self.CARDS_PER_PAGE = 25
        self.URL = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?action=advanced&set=+[%s]&page='%(setName,)
        print "setting up downloader for:", self.URL
        print "saving files for this downloader to:", self.FILENAME_PATTERN
        self.retries = 0
        
    def getNextPage(self):
        print "Attempting to get page:", self.PAGE_NUMBER, "of", self.filename
        url = self.URL + str(self.PAGE_NUMBER)
        self.scheme, self.host, self.port, self.path = client._parse(url)
        self.factory = client.HTTPClientFactory(url)
        self.factory.deferred.addCallback(self.savePage, self.factory)
        self.factory.deferred.addErrback(self.handleError, self.factory)
        reactor.connectTCP(self.host, self.port, self.factory)
        return self.factory.deferred

    def savePage(self, page, client):
        self.retries = 0
        print "Got page:", self.PAGE_NUMBER, "with status", client.status, client.message
        if int(client.status) < self.ERROR_CODE and self.PAGE_NUMBER < self.NPAGES:
            print "Trying to schedule getting the next page..."
            filename = self.FILENAME_PATTERN % (self.PAGE_NUMBER,)
            f = open(filename, "w")
            f.write(page)
            f.close()

            if self.PAGE_NUMBER == 0:
                # only do this for the first page:
                f = open(filename, "r")
                parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
                bs = parser.parse(f)
                pagingDiv = bs.find("div", {"class":"paging",})
                pageLinks = pagingDiv.findAll("a")
                # Magic offset ( - 1 ) to adjust for zero indexing
                self.NPAGES = len(pageLinks) - 1
                print "Setting number of pages in query to:", self.NPAGES
                
            self.PAGE_NUMBER += 1
            d = self.getNextPage()
            return d
        else:
            return page, client

    def handleError(self, error, client):
        print error
        if self.retries < 5:
            self.retries += 1
            print "retry", self.retries, "trying to get", self.filename, "page", self.PAGE_NUMBER
            return self.getNextPage()
        else:
            return error, client
    
deferreds = []
for setName in setNames:
    downloader = GatherSearchResultsDownloader(setName)
    deferred = downloader.getNextPage()
    deferreds.append(deferred)

def finish(ignored):
    print "shutting down after getting all pages"
    reactor.stop()

deferredList = defer.DeferredList(deferreds)
deferredList.addBoth(finish)

reactor.run()
