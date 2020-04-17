# -*- coding:UTF-8 -*-
import tushare as ts
import matplotlib.pyplot as plt
import mpl_finance as mpf
import pandas as pd
import numpy as np
import time
from datetime import date, datetime, timedelta
import talib
from stock import mytask

"""
Class Description:
    dailydata.py
    
Author:
    Ivan Ai
Created:
    2020/2/15
"""

ts.set_token('7c4d85f2c6728eb1bee17c7de4bfc61bc0a845fb62f9c8e8d3a84bcd')
pro = ts.pro_api()

pd.set_option('display.column_space', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

# font = FontProperties(fname='/Library/Fonts/Arial Unicode.ttf')
# 加这个两句 可以显示中文
plt.rcParams['font.sans-serif'] = ['STFangsong']
plt.rcParams['axes.unicode_minus'] = False

# 查询当前所有正常上市交易的股票列表，获取代码和名称对应表
all_stock_data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,name')


"""
获取上市公司股东人数，数据不定期公布
"""


def query_holder_number(ts_code, start_date, end_date):
    # 开始时间追溯至少一个季度，确保起见92天，以确期间至少有一次股东人数公布
    s_date = (datetime.strptime(start_date, '%Y%m%d') + timedelta(days=-92)).strftime("%Y%m%d")
    data = pro.stk_holdernumber(ts_code=ts_code, start_date=s_date, end_date=end_date)
    # data.sort_values(by='end_date', ascending=False, inplace=True)
    # print(data)

    dict = {data.at[index, 'end_date']: data.at[index, 'holder_num'] for index, row in data.iterrows()}
    # print(dict)

    # 获取交易所日历数据
    pd_trade_cal = pro.trade_cal(start_date=start_date, end_date=end_date)
    trade_cal_array = pd_trade_cal[pd_trade_cal['is_open'] == 1]['cal_date'].array
    print(trade_cal_array)
    final_dict = {}
    for trade_cal in trade_cal_array:
        for key in dict:
            value = dict.get(key)
            if time.strptime(trade_cal, "%Y%m%d") >= time.strptime(key, "%Y%m%d"):
                break
        final_dict[trade_cal] = value
    # print(final_dict)

    return list(final_dict.values())


"""
获取股票日线数据，画出日线图
"""


def plot_candle_line(ts_code, start_date, end_date):

    k_data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

    k_data = k_data.join(all_stock_data.set_index('ts_code'), on='ts_code')

    k_data.sort_values(by='trade_date', ascending=True, inplace=True)
    # print(k_data)

    sma_5 = talib.SMA(np.array(k_data['close']), 5)
    sma_10 = talib.SMA(np.array(k_data['close']), 10)
    sma_30 = talib.SMA(np.array(k_data['close']), 30)

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_xticks(range(0, len(k_data['trade_date']), 20))
    ax1.set_xticklabels(k_data['trade_date'][::20])
    ax1.plot(sma_5, label='MA5')
    ax1.plot(sma_10, label='MA10')
    ax1.plot(sma_30, label='MA30')
    ax1.legend(loc='upper left')

    mpf.candlestick2_ochl(ax1, k_data['open'], k_data['close'], k_data['high'], k_data['low'], width=0.5, colorup='r',
                          colordown='green', alpha=0.6)
    plt.title("个股K线图 - " + k_data.at[0, 'ts_code'] + " (" + k_data.at[0, 'name'] + ") ")
    plt.grid()
    plt.show()


"""
获取股票日线数据和股东人数数据，画出日线图和股东人数的关系图
"""


def plot_candle_line_with_holder_number(ts_code, start_date, end_date):

    k_data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

    k_data = k_data.join(all_stock_data.set_index('ts_code'), on='ts_code')

    k_data.sort_values(by='trade_date', ascending=True, inplace=True)
    # print(k_data)

    sma_5 = talib.SMA(np.array(k_data['close']), 5)
    sma_10 = talib.SMA(np.array(k_data['close']), 10)
    sma_30 = talib.SMA(np.array(k_data['close']), 30)
    holder_number = query_holder_number(ts_code=ts_code, start_date=start_date, end_date=end_date)

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_xticks(range(0, len(k_data['trade_date']), 20))
    ax1.set_xticklabels(k_data['trade_date'][::20])
    ax1.plot(sma_5, label='MA5')
    ax1.plot(sma_10, label='MA10')
    ax1.plot(sma_30, label='MA30')

    ax2 = ax1.twinx()
    ax2.plot(holder_number, label='股东人数')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    mpf.candlestick2_ochl(ax1, k_data['open'], k_data['close'], k_data['high'], k_data['low'], width=0.5, colorup='r',
                          colordown='green', alpha=0.6)
    plt.title("个股K线图 - " + k_data.at[0, 'ts_code'] + " (" + k_data.at[0, 'name'] + ") ")
    plt.grid()
    plt.show()


"""
获取个股大小单成交情况，用于辨别资金流向

小单：5万以下 中单：5万～20万 大单：20万～100万 特大单：成交额>=100万
"""


def query_moneyflow(ts_code, start_date, end_date):

    result = pro.moneyflow(ts_code=ts_code, start_date=start_date, end_date=end_date)
    result.sort_values(by='trade_date', ascending=True, inplace=True)
    result = result.join(all_stock_data.set_index('ts_code'), on='ts_code')
    # print(result)
    result['net_sm_amount'] = result['buy_sm_amount'] - result['sell_sm_amount']
    result['net_md_amount'] = result['buy_md_amount'] - result['sell_md_amount']
    result['net_lg_amount'] = result['buy_lg_amount'] - result['sell_lg_amount']
    result['net_elg_amount'] = result['buy_elg_amount'] - result['sell_elg_amount']
    # 我们假定主力资金只包括大单和超大单
    result['net_cm_amount'] = result['net_lg_amount'] + result['net_elg_amount']
    # print(result)
    # result.to_csv("/Users/ivan/result.csv")

    vol_result = result[['ts_code', 'name', 'trade_date', 'buy_sm_vol', 'sell_sm_vol', 'buy_md_vol', 'sell_md_vol', 'buy_lg_vol', 'sell_lg_vol', 'buy_elg_vol', 'sell_elg_vol']]
    # print(vol_result)
    # amount_result = result[['ts_code', 'name', 'trade_date', 'buy_sm_amount', 'sell_sm_amount', 'buy_md_amount', 'sell_md_amount', 'buy_lg_amount', 'sell_lg_amount', 'buy_elg_amount', 'sell_elg_amount', 'net_mf_amount']]
    # print(amount_result)
    net_amount_result = result[['ts_code', 'name', 'trade_date', 'net_sm_amount', 'net_md_amount', 'net_lg_amount', 'net_elg_amount', 'net_cm_amount']]
    # print(net_amount_result)

    return vol_result, net_amount_result


"""
以表格和图分析和展示个股小单、中单、大单、特大单买入卖出详情，默认输出最近20个交易日
"""


def analyze_moneyflow(ts_code, start_date, end_date, plot=False):
    lst_result = query_moneyflow(ts_code, start_date, end_date)

    vol_result = lst_result[0]
    print(vol_result.tail(10))

    net_amount_result = lst_result[1]
    print(net_amount_result.tail(10))

    k_data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    k_data = k_data.join(all_stock_data.set_index('ts_code'), on='ts_code')
    k_data.sort_values(by='trade_date', ascending=True, inplace=True)
    # print(k_data)

    # 画图展示个股小单、中单、大单、特大单买入卖出详情
    if plot:
        fig = plt.figure(figsize=(15, 7))
        fig.subplots_adjust(left=0.14, right=0.96, bottom=0.10, top=0.96)

        ax1 = fig.add_subplot(311)
        net_amount_result.plot.bar(x='trade_date', y=['net_sm_amount', 'net_md_amount', 'net_lg_amount', 'net_elg_amount', 'net_cm_amount'], ax=ax1)
        ax1.set_title(
            "个股资金流向图（基于成交金额 - 小单：5万以下；中单：5万～20万；大单：20万～100万；特大单：成交额>=100万）- " + vol_result.at[1, 'ts_code'] + " (" + vol_result.at[0, 'name'] + ") ")
        ax1.set_xlabel("")
        ax1.get_legend().set_bbox_to_anchor((-0.045, 1.02))

        ax2 = fig.add_subplot(312, sharex=ax1)
        ax2.plot(np.array(k_data['close']), label='close')
        mpf.candlestick2_ochl(ax2, k_data['open'], k_data['close'],k_data['high'], k_data['low'], width=0.5,
                              colorup='r',
                              colordown='green', alpha=0.6)
        ax2.set_xlabel("")

        for tick in ax2.get_xticklabels():
            tick.set_rotation(90)

        ax3 = fig.add_subplot(313, sharex=ax1)
        vol_result.plot.bar(x='trade_date', y=['buy_sm_vol', 'sell_sm_vol', 'buy_md_vol', 'sell_md_vol', 'buy_lg_vol', 'sell_lg_vol', 'buy_elg_vol', 'sell_elg_vol'], ax=ax3)
        # ax1.set_title(
        #     "个股资金流向图（基于成交量 - 小单：5万以下；中单：5万～20万；大单：20万～100万；特大单：成交额>=100万）- " + vol_result.at[1, 'ts_code'] + " (" + vol_result.at[0, 'name'] + ") ")
        ax3.set_xlabel("")
        ax3.get_legend().set_bbox_to_anchor((-0.055, 1.02))

        plt.show()


if __name__ == '__main__':

    # # 2019年的妖股及其背后的股东变化情况 - start
    # begin = '20140501'
    # end = '20200501'
    #
    # # stock_list = ['600776.SH', '000723.SZ', '002565.SZ', '002356.SZ', '300748.SZ']
    # stock_list = ['600876.SH']
    # for ts_code in stock_list:
    #     plot_candle_line_with_holder_number(ts_code, begin, end)
    #     # plot_candle_line(ts_code, begin, end)
    # # 2019年的妖股及其背后的股东变化情况 - end

    # 个股资金流向 - start
    begin = '20200301'
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y%m%d")

    stock_list = ['002120.SZ']
    for ts_code in stock_list:
    # for ts_code in mytask.MY_STOCK_LIST:
        analyze_moneyflow(ts_code, begin, yesterday, True)
    # 个股资金流向 - end
