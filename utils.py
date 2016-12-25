#!/usr/bin/python2
# -*- coding: utf-8 -*-

import datetime

def getAllMonth():
    now = datetime.datetime.now()
    now_month = now.strftime("%Y%m")[2:]
    return [now_month,getNextMonth(1),getNextMonth(3),getNextMonth(6)]

def getNextMonth(addon):
    today=datetime.datetime.today()
    year=today.year
    month=today.month
    month += addon
    if month > 12:
        month -= 12
        year+=1
    res=datetime.datetime(year,month,1)
    return res.strftime("%Y%m")[2:]