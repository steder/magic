import time
import urllib
import sqlite3

import html5lib
from html5lib import treebuilders

from twisted.web import client
from twisted.internet import defer
from twisted.internet import reactor

class GatherImages(object):
    def __init__(self):
        self.connection = sqlite3.connect("magic.db")
        self.count = self.connection.cursor()
        self.query = self.connection.cursor()
        self.query.execute("select multiverseid from cards where image is null;")
        self.update = self.connection.cursor()
        self.ERROR_CODE = 400
        self.OK = 200
        self.URL = "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=%s&type=card"
        self.retries = 0

    def missingImageCount(self):
        self.count.execute("select count() from cards where image is null;")
        missingCount = int(self.count.fetchone()[0])
        print "missing %s images"%(missingCount)
        return missingCount
        
    def getNextImage(self):
        self.multiverseid = str(self.query.fetchone()[0])
        url = self.URL % (self.multiverseid)
        print "fetching:", self.multiverseid, "@", url
        self.scheme, self.host, self.port, self.path = client._parse(url)
        self.factory = client.HTTPClientFactory(url)
        self.factory.deferred.addCallback(self.saveImage, self.factory)
        self.factory.deferred.addErrback(self.handleError, self.factory)
        reactor.connectTCP(self.host, self.port, self.factory)
        return self.factory.deferred

    def saveImage(self, page, client):
        print "success status:", client.status
        self.retries = 0
        if int(client.status) == self.OK:
            self.update.execute("update cards set image = ? where multiverseid = ?;", (sqlite3.Binary(page), self.multiverseid))
            self.connection.commit()
        return page, client
    
    def handleError(self, error, client):
        print "error status:", client.status
        print error
        return error, client

    def finish(self, ignored):
        if self.missingImageCount() > 0:
            d = self.getNextImage()
            d.addBoth(self.finish)
            return d
        print "shutting down after getting all pages"
        self.connection.commit()
        self.query.close()
        self.update.close()
        reactor.stop()
    
deferreds = []
downloader = GatherImages()
deferred = downloader.getNextImage()
deferreds.append(deferred)

deferredList = defer.DeferredList(deferreds)
deferredList.addBoth(downloader.finish)

reactor.run()
