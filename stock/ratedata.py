# -*- coding:UTF-8 -*-
import tushare as ts
import matplotlib.pyplot as plt
from datetime import date, timedelta

"""
Class Description:
    ratedata.py
    
Author:
    Ivan Ai
Created:
    2020/3/23
"""

ts.set_token('7c4d85f2c6728eb1bee17c7de4bfc61bc0a845fb62f9c8e8d3a84bcd')
pro = ts.pro_api()

"""
获取SHIBOR利率数据
"""


def query_shibor(start_date, end_date, plot=False):

    result = pro.shibor(start_date=start_date, end_date=end_date)
    result.sort_values(by='date', ascending=True, inplace=True)
    print(result.tail(10), "\n")

    # 画图展示SHIBOR
    if plot:
        ax = result.plot.line(x='date', y=['on', '1w', '1m', '3m', '6m', '1y'], figsize=(15, 6))
        ax.set_xlabel("")
        plt.title(
            "The trend of Shanghai Interbank Offered Rate ")
        plt.show()


"""
获取LIBOR利率数据
"""


def query_libor(start_date, end_date, plot=False):

    result = pro.libor(start_date=start_date, end_date=end_date)
    result.sort_values(by='date', ascending=True, inplace=True)
    print(result.tail(10), "\n")

    # 画图展示LIBOR
    if plot:
        ax = result.plot.line(x='date', y=['on', '1w', '1m', '3m', '6m', '12m'], figsize=(15, 6))
        ax.set_xlabel("")
        plt.title(
            "The trend of London Interbank Offered Rate ")
        plt.show()


"""
获取HIBOR利率数据
"""


def query_hibor(start_date, end_date, plot=False):

    result = pro.hibor(start_date=start_date, end_date=end_date)
    result.sort_values(by='date', ascending=True, inplace=True)
    print(result.tail(10), "\n")

    # 画图展示HIBOR
    if plot:
        ax = result.plot.line(x='date', y=['on', '1w', '1m', '3m', '6m', '12m'], figsize=(15, 6))
        ax.set_xlabel("")
        plt.title(
            "The trend of Hongkong Interbank Offered Rate ")
        plt.show()


"""
获取SHIBOR LPR利率数据
"""


def query_shibor_lpr(start_date, end_date, plot=False):

    result = pro.shibor_lpr(start_date=start_date, end_date=end_date)
    result.sort_values(by='date', ascending=True, inplace=True)
    print(result.tail(10), "\n")

    # 画图展示SHIBOR LPR
    if plot:
        ax = result.plot.line(x='date', y=['1y'], figsize=(15, 6))
        ax.set_xlabel("")
        plt.title("The trend of Loan Prime Rate ")
        plt.show()

"""
获取美国每日国债收益率曲线利率
"""


def query_us_government_bonds_return_rate(start_date, end_date, plot=False):

    result = pro.us_tycr(start_date=start_date, end_date=end_date)
    result.sort_values(by='date', ascending=True, inplace=True)
    print(result.tail(10), "\n")

    # 画图展示HIBOR
    if plot:
        ax = result.plot.line(x='date', y=['m1', 'm3', 'm6', 'y1', 'y5', 'y10'], figsize=(15, 6))
        ax.set_xlabel("")
        plt.title(
            "The trend of US Government Bonds Return Rate ")
        plt.show()


if __name__ == '__main__':
    begin = '20200101'
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y%m%d")

    query_shibor(begin, yesterday, True)
    # query_libor(begin, yesterday, True)
    # query_hibor(begin, yesterday, True)
    # query_shibor_lpr(begin, yesterday, True)
    query_us_government_bonds_return_rate(begin, yesterday, True)