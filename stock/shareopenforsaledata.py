# -*- coding:UTF-8 -*-
import tushare as ts
import pandas as pd
from datetime import datetime, date, timedelta

"""
Class Description:
    shareopenforsaledata.py
    
Author:
    Ivan Ai
Created:
    2019/12/11
"""

ts.set_token('7c4d85f2c6728eb1bee17c7de4bfc61bc0a845fb62f9c8e8d3a84bcd')
pro = ts.pro_api()

pd.set_option('display.column_space', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)

today = date.today().strftime("%Y%m%d")
yesterday = (date.today() + timedelta(days=-1)).strftime("%Y%m%d")

# 查询当前所有正常上市交易的股票列表，获取代码和名称对应表
all_stock_data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,name')

"""
获取最近n天的限售股解禁数据
根据相关法规，上市公司董事会应该在限售股解禁3个交易日内发提示性公告
同时有新股发行或增发，也会产生限售股解禁公告，此类公告的限售股解禁日期可能1年或2年甚至3年后
Tushare获取限售股数据包含这部分数据，需要从数据集中剔除掉
"""


def query_share_float(days=30):
    start_date = date.today() + timedelta(days=-days)
    date_ser = pd.date_range(start_date, periods=days)
    date_array = date_ser.tolist()

    result = []
    for day in date_array:
        print(day.strftime("%Y%m%d"))
        df = pro.share_float(ann_date=day.strftime("%Y%m%d"))
        if len(df) > 0:
            result.append(df)

    if len(result) == 0:
        return None

    pd_result = pd.concat(result)

    # pd_temp = pd_result[pd_result['ts_code'].isin(['603036.SH'])]
    # print(pd_temp)
    # print(pd_temp.duplicated())

    # 法规规定解禁前3个交易日内发提示性公告，放宽到30日以过滤1年或2年后解禁的公告
    m = pd.to_datetime(pd_result['float_date']).le(pd.to_datetime(pd_result['ann_date']) + pd.Timedelta(30, unit='D'))
    pd_filter_result = pd_result[m]

    pd_join_result = pd_filter_result.join(all_stock_data.set_index('ts_code'), on='ts_code')

    # 将name列提到ts_code列后
    # name_col = pd_final_result['name']
    # pd_final_result.drop(labels=['name'], axis=1, inplace=True)
    # pd_final_result.insert(1, 'name', name_col)
    pd_final_result = pd_join_result.reindex(
        ['ts_code', 'name', 'ann_date', 'float_date', 'float_share', 'float_ratio', 'holder_name', 'share_type'],
        axis='columns')

    return pd_final_result


if __name__ == '__main__':

    ret = query_share_float(days=60)
    print(ret)
    print("==============================================\n")
    if ret is not None:
        g_ret = ret.groupby(['ts_code', 'name', 'ann_date']).sum()
        g_ret.sort_values(by='ann_date', ascending=True, inplace=True)
        print(g_ret)
