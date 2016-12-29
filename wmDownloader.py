# -*- coding: utf-8 -*-

from dataapiclient import Client
import pandas as pd
import json
import datetime
import math
import sys
import leveldb
reload(sys)
sys.setdefaultencoding('utf-8')

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

    db = leveldb.LevelDB("db/kv", create_if_missing=True)
    last_update_date = None
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        last_update_date = db.Get("update_time")
    except Exception, e:
        print e

    if read_cache and today == last_update_date:
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
            db.Put("update_time",today)
            return df
        else:
            print(jsonObj)
    else:
        print(code)
        print(result)

def getAllMonth():
    now = datetime.datetime.now()
    options_info = getOptionsInfo(True)
    options_info = options_info.drop_duplicates(["exerDate"])
    exer_date_se = options_info["exerDate"]
    exer_date_se = pd.to_datetime(exer_date_se)
    future_dates = exer_date_se[exer_date_se > now]
    future_dates.sort()
    return [date.strftime("%Y%m")[2:] for date in list(future_dates)]

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

    # today = datetime.datetime.now()
    # for i in range(0,400):
    #     day = today - datetime.timedelta(days = i)
    #     daystr = day.strftime("%Y%m%d")
    #     df = getHistoryQuotesInfo(daystr)