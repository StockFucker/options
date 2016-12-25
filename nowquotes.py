#!/usr/bin/python2
# -*- coding: utf-8 -*-

import pandas as pd
import urllib2
import sys   
import datetime
from sina_parser import Parser
from wmDownloader import getOptionsInfo
from utils import getAllMonth

class download:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0'
        self.headers = {'User-Agent': self.user_agent, 'Accept-encoding':'gzip, deflate'}
        self.opener = urllib2.build_opener()
        self.base_url = "http://hq.sinajs.cn/list="
        self.encodetype = sys.getfilesystemencoding()
        self.target = "510050"


    def getofMonth(self,month,direction):
        url = "OP_"+direction+"_"+self.target+month
        response = self.get(url)
        items = Parser.extractDataSingle(response)
        response = self.get(items)
        data = Parser.extractMultipleOptionData(response)
        return data

    def getItemsOfMonth(self,month,direction):
        url = "OP_"+direction+"_"+self.target+month
        response = self.get(url)
        items = Parser.extractDataSingle(response)
        return items

    @property
    def targetPrice(self):
        url = "sh"+self.target
        response = self.get(url)
        data = Parser.extractSingleETFData(response)
        return data["now"]
        
    def get(self, url):
        # print('Downloading: %s' % url)
        request = urllib2.Request(self.base_url+url)
        response = self.opener.open(request)
        html = response.read()
        return unicode(html, "gb2312").encode("utf8")

    @property
    def all(self):
        months = getAllMonth()
        ups = []
        downs = []
        for month in months:
            up_data = self.getofMonth(month,"UP")
            down_data = self.getofMonth(month,"DOWN")
            ups.append(pd.DataFrame(up_data).T)
            downs.append(pd.DataFrame(down_data).T)
        data = ups + downs
        return data

if __name__ == '__main__':
    download = download()
    print(download.all)
    # print(download.targetPrice)

