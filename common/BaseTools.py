#!/usr/bin/python
#coding=utf-8

'''
工具类

'''

import datetime
from datetime import timedelta
import MySQLdb
import pandas as pd

'''
获取mysql的链接
'''
def getConnection():
    # conn = MySQLdb.connect(host='192.168.2.31', user='root', passwd='1qaz@WSX+!', db='strategy', port=3306)
    conn = MySQLdb.connect(host='115.28.128.166', user='invicme', passwd='invicme', db='test', port=3306, charset="utf8")
    return conn

def getTradeDay(conn, start_date_str=None, end_date_str=None, type=1):
    tradedaySql = "select tradedate from sys_tradeday where type = "+str(type)
    if start_date_str:
        tradedaySql += " and tradedate>=date_format('" + start_date_str + "', '%Y-%m-%d')"
    if end_date_str:
        tradedaySql += " and tradedate<=date_format('" + end_date_str + "', '%Y-%m-%d')"
    else:
        tradedaySql += " and tradedate<=now()"

    tradedaySql += " order by tradedate asc"
    #print tradedaySql
    tradedayDf = pd.read_sql(tradedaySql, conn)
    return tradedayDf

def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        #print dt.weekday()
        date = dt.strftime("%Y-%m-%d")
    return dates

'''
获取最近的季度日期
'''
def getLastestQuarterlistByDate(d):
    year = d.year
    month = d.month
    day = d.day
    # print year, month, day
    quarter=[]
    if month <= 12 and month > 9:
        quarter.append((year, 3))
        quarter.append((year, 2))
        quarter.append((year, 1))
    elif month <= 9 and month > 6:
        quarter.append((year, 2))
        quarter.append((year, 1))
        quarter.append((year-1, 4))
    elif month <= 6 and month > 3:
        quarter.append((year, 1))
        quarter.append((year-1, 4))
        quarter.append((year-1, 3))
    elif month <= 3 and month > 0:
        quarter.append((year-1, 4))
        quarter.append((year-1, 3))
        quarter.append((year-1, 2))
    return quarter

def getDateByQuarter(year, quarter):
    month = 0
    day = 0
    if quarter == 1:
        month = 3
        day = 31
    elif quarter == 2:
        month = 6
        day = 30
    elif quarter == 3:
        month = 9
        day = 30
    elif quarter == 4:
        month = 12
        day = 31
    d = datetime.date(year, month, day)
    return d

'''
查询两个时间段中的季度
'''
def getQuarterlistByDate(start_date, end_date):
    startQuarterlist = getLastestQuarterlistByDate(start_date)
    endQuarterlist = getLastestQuarterlistByDate(end_date)
    quarterlist = []
    for q in endQuarterlist:
        quarterlist.append(q)
    while endQuarterlist[2] not in startQuarterlist:
        d = getDateByQuarter(endQuarterlist[2][0], endQuarterlist[2][1])
        endQuarterlist = getLastestQuarterlistByDate(d + timedelta(days=-1))
        for q in endQuarterlist:
            quarterlist.append(q)
    for d in startQuarterlist:
        if d in quarterlist:
            continue
        quarterlist.append(d)
    return quarterlist

'''
交集
'''
def intersection(list1, list2):
    ret_list = list((set(list1).union(set(list2))) ^ (set(list1) ^ set(list2)))
    return ret_list

'''
并集
'''
def union(list1, list2):
    ret_list = list(set(list1).union(set(list2)))
    return ret_list

'''
差集
'''
def difference(list1, list2):
    ret_list = []
    for item in list1:
        if item not in list2:
            ret_list.append(item)
    return ret_list

if __name__ == '__main__':
    print dateRange("2016-01-01", "2016-02-01")
    conn = getConnection()
    c = conn.cursor()
    sql = "select * from r_strategy"
    c.execute(sql)
    alldata = c.fetchall()
    print alldata

    print getLastestQuarterlistByDate(datetime.datetime.now())

    print getDateByQuarter(2017, 3)

    print getQuarterlistByDate(datetime.date(2016, 1, 15), datetime.date(2017, 8, 27))

    dict = {"a": ("apple",), "bo": {"b": "banana", "o": "orange"}, "g": ["grape", "grapefruit"]}
    print dict.values()