# -*- coding:UTF-8 -*-
import tushare as ts
import pandas as pd

"""
Class Description:
    funddata.py
    
Author:
    Ivan Ai
Created:
    2019/12/30
"""

ts.set_token('7c4d85f2c6728eb1bee17c7de4bfc61bc0a845fb62f9c8e8d3a84bcd')
pro = ts.pro_api()

pd.set_option('display.column_space', 100)
pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.width', 1000)

"""
获取公募基金数据列表，包括E（场内）O（场外）默认E
"""


def query_fund_basic(market='E'):
    result = pro.fund_basic(market=market)

    return result


if __name__ == '__main__':
    ret = query_fund_basic()
    print(ret)
    print(ret[ret['status'] == 'D'])
