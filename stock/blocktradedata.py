# -*- coding:UTF-8 -*-
import tushare as ts
import pandas as pd
from datetime import date

"""
Class Description:
    blocktradedata.py
    
Author:
    Ivan Ai
Created:
    2019/12/24
"""

ts.set_token('7c4d85f2c6728eb1bee17c7de4bfc61bc0a845fb62f9c8e8d3a84bcd')
pro = ts.pro_api()

pd.set_option('display.column_space', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

"""
获取个股大宗交易数据
"""


def query_block_trade_data(ts_code, start_date, end_date):
    result = pro.block_trade(ts_code=ts_code, start_date=start_date, end_date=end_date)

    return result


if __name__ == '__main__':
    begin = '20191001'
    today = date.today().strftime("%Y%m%d")
    ts_code = '002601.SZ'

    ret = query_block_trade_data(ts_code, begin, today)
    print(ret)
    print("vol: ", ret.vol.sum(), ", amount: ", ret.amount.sum())
