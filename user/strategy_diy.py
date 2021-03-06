#!/usr/bin/python
#coding=utf-8

'''
策略-diy

'''

import common.Constants as cc
import common.Basedata as cb
import common.BaseTools as cbt
import common.StrategyTools as cst
import common.TushareBasedata as TushareBasedata
import common.TechFactorService as TechFactorService
import common.StockOrder as StockOrder


from datetime import datetime

'''
## 初始化函数，设定要操作的股票、基准等等
'''
def init():
    # 周期类型 ：D、天 W、周 M、月
    cc.periodType = 'D'
    cc.changePeriod = 20
    cc.startDateStr='2016-4-1'
    cc.endDateStr='2017-4-1'
    cc.initMoney=1000000


## 股票筛选初始化函数
def getStockList():
    tbd = TushareBasedata.TushareBasedata()
    # 000016.SH：上证50   沪深300：000300.SH 创业板：399006.SZ 中证500：000905.SH
    stocklist1 = tbd.get_stocklist_by_type('', '000300.SH')
    stocklist2 = tbd.get_stocklist_by_type('', '000905.SH')

    '''
    industryDf = tbd.get_stock_data_by_industryname()
    conceptDf = tbd.get_stock_data_by_conceptname()
    areaDf = tbd.get_stock_data_by_areaname()
    '''
    return stocklist1+stocklist2

## 股票筛选排序初始化函数


## 出场初始化函数

## 入场初始化函数

## 风控初始化函数

## 卖出未卖出成功的股票

'''
风控
卖出股票......
def riskcontrol():
    pass
'''

## 股票筛选


## 交易函数
def trade(tradedate):
    '''
    调仓周期
    '''
    conn = cbt.getConnection()
    # 如果当前没有到调仓周期,跳过
    if cc.currentPeriod!=cc.changePeriod:
        cc.currentPeriod = cc.currentPeriod+1
        return
    cc.currentPeriod = 1
    # 获取票池
    stocklist = getStockList()
    if len(stocklist) == 0:
        return
    price = 0
    positionList = cc.positionList
    '''
    通过买入条件获取买入股票,取并集或者交集
    '''
    techFactor = TechFactorService.TechFactorService()
    # 传入股票池、收盘价标识、交易日期、5日、10日、金叉参数
    stocklist1 = techFactor.ma(stocklist, 'close', tradedate, 5, 10, 1)
    t = TushareBasedata.TushareBasedata()
    trade_date_str = datetime.strftime(tradedate, '%Y-%m-%d')
    # 穿入股票，查询股票的市值因子列表，mv
    df = t.get_factor_data_by_stocklist(trade_date_str, stocklist, 'roe', 0)
    # 按因子排序，计算得到前10%的股票代码
    df = df.sort_values(by='fv')
    stocklist2 = df.code.tolist()
    # 取并集
    stocklist = stocklist1+stocklist2
    # 订单列表
    orderlist = []

    '''
    调整仓位：卖出不在票池的股票
    '''
    # 卖出
    for position in positionList:
        code = position.code
        if code in stocklist:
            stocklist.remove(code)
            continue
        # cst.order(tradedate, code, price, 0)
        o = StockOrder.StockOrder(cc.strategyId, code, tradedate, price, 0)
        orderlist.append(o)

    '''
    调整仓位：买入符合条件的股票
    '''
    # 买入
    for code in stocklist:
        o = StockOrder.StockOrder(cc.strategyId, code, tradedate, price, 100)
        orderlist.append(o)
    # 订单入库，并更新仓位
    cst.order(orderlist, conn)

    if len(orderlist) == 0:
        return 0
    return 1



##################################  选股函数群 ##################################

###################################  公用函数群 ##################################
## 排序
def check_stocks_sort(context, security_list, input_dick, ascending='desc'):
    pass


## 过滤同一标的继上次卖出N天不再买入
def filter_n_tradeday_not_buy(security, n=0):
    pass


## 是否可重复买入
def holded_filter(context, security_list):
    pass


## 卖出股票加入dict
def selled_security_list_dict(context, security_list):
    pass


## 过滤停股票
def paused_filter(context, security_list):
    return security_list


## 过滤退市股票
def delisted_filter(context, security_list):
    return security_list


## 过滤ST股票
def st_filter(context, security_list):
    return security_list


# 过滤涨停股票
def high_limit_filter(context, security_list):
    pass

'''
交易前
'''
def startTrade(d):
    pass


'''
交易后
1、初始化或记录当日资金账户信息
2、如果没有订单，查询最新的仓位交易日, 如果仓位交易日为空，初始化资金账户,
   如果仓位交易日不为空，查询仓位信息，复制仓位信息到新的交易日

'''
def endTrade(d, flag):
    conn = cbt.getConnection()
    # 查询最新的交易日
    lastAccountDateStr = cst.getLastAccountDate(cc.strategyId, conn)
    # 记录资金账户信息
    money = cc.initMoney + cc.tradeMoney
    cst.saveAccount(cc.strategyId, d, money, conn)
    cc.tradeMoney=0
    # 如果没有订单，查询最新的仓位交易日
    if flag == 0:
        # 如果仓位交易日不为空，查询仓位信息，复制仓位信息到新的交易日
        if lastAccountDateStr != None:
            lastPositionDf = cst.getPositionList(cc.strategyId, lastAccountDateStr, conn)
            if len(lastPositionDf) > 0:
                positionDf = lastPositionDf.copy()
                # 更新仓位日期
                positionDf['TRADEDATE'] = d
                positionList = [tuple(x) for x in positionDf.values]
                cst.savePosition(positionList, conn)

'''
日交易
'''
def handle_data(d):
    print d
    startTrade(d)
    i = trade(d)
    endTrade(d, i)