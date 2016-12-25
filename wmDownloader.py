# -*- coding: utf-8 -*-

from dataapiclient import Client
import pandas as pd
import json
import datetime
import math
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

wmclient = Client()
wmclient.init('affc55288f98b25893ba0bd134810d5b60a99c99966c1a316abcbbf5bae2dd5c')

def getIndexQuotesInfo(read_cache=False):
    if read_cache:
        df = pd.read_csv("index_quotes_info.csv",parse_dates=True)
        df = df.set_index(["tradeDate"])
        return df;

    global wmclient
    url1='/api/market/getMktFundd.json?field=&beginDate=&endDate=&secID=510050.XSHG&ticker=&tradeDate='
    code, result = wmclient.getData(url1)
    if code==200:
        jsonObj = json.loads(result)
        if jsonObj['retCode'] == 1:
            data_bag = json.loads(json.dumps(jsonObj['data']))
            df = pd.DataFrame(data_bag)
            df = df.set_index(["tradeDate"])
            df.to_csv("index_quotes_info.csv")
            return df
        else:
            print(jsonObj)
    else:
        print(code)
        print(result)

def getOptionsInfo(read_cache=False):
    if read_cache:
        df = pd.read_csv("options_info.csv",dtype={"optID":str})
        df = df.set_index(["optID"])
        return df;

    global wmclient
    url1='/api/options/getOpt.json?field=&secID=&optID=&ticker=&varSecID=510050.XSHG&varticker=&contractStatus='
    code, result = wmclient.getData(url1)
    if code==200:
        jsonObj = json.loads(result)
        if jsonObj['retCode'] == 1:
            data_bag = json.loads(json.dumps(jsonObj['data']))
            df = pd.DataFrame(data_bag)
            df = df.set_index(["optID"])
            df.to_csv("options_info.csv")
            return df
        else:
            print(jsonObj)
    else:
        print(code)
        print(result)

def getHistoryQuotesInfo(date,read_cache=False):

    filePath = "history/" + date + ".csv"

    if read_cache:
        df = pd.read_csv(filePath,dtype={"optID":str})
        df = df.set_index(["optID"])
        return df;

    global wmclient
    url1='/api/market/getMktOptd.json?field=&secID=&optID=&beginDate=&endDate=&ticker=&tradeDate=' + date
    code, result = wmclient.getData(url1)
    if code==200:
        jsonObj = json.loads(result)
        if jsonObj['retCode'] == 1:
            data_bag = json.loads(json.dumps(jsonObj['data']))
            df = pd.DataFrame(data_bag)
            df = df.set_index(["optID"])
            df.to_csv(filePath)
            return df
        else:
            print(jsonObj)
    else:
        print(code)
        print(result)

if __name__ == '__main__':
    # print fetchStockQuotes(['000001','000002','000003'])
    # print(getRankData(['600099','002057','600781']))
    print(getOptionsInfo())
    print(getIndexQuotesInfo())

    today = datetime.datetime.now()
    for i in range(0,400):
        day = today - datetime.timedelta(days = i)
        daystr = day.strftime("%Y%m%d")
        df = getHistoryQuotesInfo(daystr)