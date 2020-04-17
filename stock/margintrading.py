# -*- coding:UTF-8 -*-
import tushare as ts
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, timedelta
from stock import mytask

"""
Class Description:
    margintrading.py
    
Author:
    Ivan Ai
Created:
    2020/2/5
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
获取个股的融资融券数据，并返回合并信息的pandas dataframe格式以便分析
"""


def query_margin_detail_for_single_stock(ts_code, start_date, end_date):
    exchange = ts_code[-2:]
    # 获取融资融券交易数据
    data = pro.margin_detail(ts_code=ts_code, start_date=start_date, end_date=end_date, exchange=exchange)
    data.sort_values(by='trade_date', ascending=True, inplace=True)
    # print(data)

    join_data = data.join(all_stock_data.set_index('ts_code'), on='ts_code')

    result = join_data.reindex(['trade_date', 'ts_code', 'name', 'rzye', 'rzmre', 'rzche'], axis='columns')

    return result


"""
以表格和图分析和展示个股融资融券数据，默认输出最近20个交易日数据
"""


def analyze_margin_data_for_single_stock(ts_code, start_date, end_date, plot=False):
    result = query_margin_detail_for_single_stock(ts_code, start_date, end_date)

    # 修改列名
    result.columns = ['trade_date', 'ts_code', 'name', 'margin balance', 'buying on margin', 'selling on margin']
    # print(result.tail(20), "\n")

    # 获取日线行情
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df.sort_values(by='trade_date', ascending=True, inplace=True)
    # print(df.tail(20), "\n")

    # result = pd.concat([result, df[['close', 'open', 'high', 'low', 'pct_chg']]], axis=1)
    result = result.join(df.set_index(['trade_date', 'ts_code']), on=['trade_date', 'ts_code'])

    # 打印最近融资融券数据
    print(result.tail(20), "\n")

    # 画图展示融资买入和偿还额以及融资余额趋势
    if plot:
        fig = plt.figure(figsize=(15, 7))

        ax1 = fig.add_subplot(211)
        result.plot(x='trade_date', y=['margin balance', 'close'], secondary_y=['close'], ax=ax1)
        ax1.set_title(
            "个股融资余额和收盘价图 - " + result.at[0, 'ts_code'] + " (" + result.at[0, 'name'] + ") ")
        ax1.set_xlabel("")

        ax2 = fig.add_subplot(212)
        result.plot(x='trade_date', y=['margin balance', 'buying on margin', 'selling on margin'], secondary_y=['buying on margin', 'selling on margin'], ax=ax2)
        ax2.set_title(
            "个股融资余额以及融资买入和融资偿还数据图 - " + result.at[0, 'ts_code'] + " (" + result.at[0, 'name'] + ") ")
        ax2.set_xlabel("")

        plt.show()

"""
获取全市场的融资融券数据，并返回合并信息的pandas dataframe格式以便分析
"""


def query_margin_for_whole_market(start_date, end_date):

    # 获取融资融券交易数据
    result = pro.margin(start_date=start_date, end_date=end_date)
    result.sort_values(by='trade_date', ascending=True, inplace=True)
    # print(result)

    return result


"""
以表格和图分析和展示全市场融资融券数据，默认输出最近20个交易日数据
"""


def analyze_margin_data_for_whole_market(start_date, end_date, plot=False):
    result = query_margin_for_whole_market(start_date, end_date)

    # 修改列名
    result.columns = ['trade_date', 'exchange', 'margin balance', 'buying on margin', 'selling on margin', 'securities balance', 'buying on securities', 'selling on securities']
    # print(result.tail(10), "\n")

    # 分割沪深两市融资融券数据
    sh_data = result[result['exchange'] == 'SSE']
    # print(sh_data.tail(10), "\n")
    sh_data = sh_data[['trade_date', 'margin balance', 'buying on margin', 'selling on margin']]
    sh_data.columns = ['trade_date', 'margin balance(SH)', 'buying on margin(SH)', 'selling on margin(SH)']
    sh_data.reset_index(drop=True, inplace=True)
    # print(sh_data.tail(10), "\n")

    sz_data = result[result['exchange'] == 'SZSE']
    # print(sz_data.tail(10), "\n")
    sz_data = sz_data[['trade_date', 'margin balance', 'buying on margin', 'selling on margin']]
    sz_data.columns = ['trade_date', 'margin balance(SZ)', 'buying on margin(SZ)', 'selling on margin(SZ)']
    sz_data.reset_index(drop=True, inplace=True)
    # print(sz_data.tail(10), "\n")

    com_data = pd.concat([sh_data, sz_data[['margin balance(SZ)', 'buying on margin(SZ)', 'selling on margin(SZ)']]], axis=1)
    # print(com_data.tail(10), "\n")

    sum_data = com_data.copy()
    sum_data['margin balance(total)'] = sum_data['margin balance(SH)'] + sum_data['margin balance(SZ)']
    sum_data['buying on margin(total)'] = sum_data['buying on margin(SH)'] + sum_data['buying on margin(SZ)']
    sum_data['selling on margin(total)'] = sum_data['selling on margin(SH)'] + sum_data['selling on margin(SZ)']
    print(sum_data.tail(10), "\n")

    # 画图展示融资买入和偿还额以及融资余额趋势
    if plot:
        fig = plt.figure(figsize=(15, 8))
        fig.subplots_adjust(left=0.18, right=0.96, bottom=0.10, top=0.96)

        ax1 = fig.add_subplot(211)
        sum_data.plot.bar(x='trade_date', y=['margin balance(total)', 'buying on margin(total)', 'selling on margin(total)'], secondary_y=['buying on margin(total)', 'selling on margin(total)'], ax=ax1)
        ax1.set_title(
            "沪深两市融资余额以及融资买入和融资偿还数据图 - 汇总")
        ax1.set_xlabel("")
        ax1.get_legend().set_bbox_to_anchor((-0.025, 1.02))

        ax2 = fig.add_subplot(212)
        com_data.plot.bar(x='trade_date', y=['margin balance(SH)', 'buying on margin(SH)', 'selling on margin(SH)', 'margin balance(SZ)', 'buying on margin(SZ)', 'selling on margin(SZ)'], secondary_y=['buying on margin(SH)', 'selling on margin(SH)', 'buying on margin(SZ)', 'selling on margin(SZ)'], ax=ax2)
        ax2.set_title(
            "沪深两市融资余额以及融资买入和融资偿还数据图 - 分市场 ")
        ax2.set_xlabel("")
        ax2.get_legend().set_bbox_to_anchor((-0.025, 1.02))

        plt.show()


if __name__ == '__main__':
    begin = '20200201'
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y%m%d")

    # stock_list = ['601328.SH', '000898.SZ', '600835.SH', '000538.SZ', '600009.SH', '601318.SH', '002120.SZ',
    #               '002372.SZ', '300024.SZ', '002601.SZ', '600597.SH', '601877.SH', '600066.SH', '600406.SH',
    #               '002027.SZ', '000776.SZ', '000002.SZ', '000878.SZ', '300124.SZ', '600498.SH', '600104.SH',
    #               '000651.SZ']
    # stock_list = ['601328.SH']
    for ts_code in mytask.MY_STOCK_LIST:
        analyze_margin_data_for_single_stock(ts_code, begin, yesterday, True)

    analyze_margin_data_for_whole_market(begin, yesterday, True)
