# -*- coding:UTF-8 -*-
from datetime import date, timedelta
from stock import hkholddata, margintrading, dailydata, ratedata

"""
Class Description:
    mytask.py
    
Author:
    Ivan Ai
Created:
    2020/4/6
"""

MY_STOCK_LIST = ['601328.SH', '000898.SZ', '600835.SH', '601877.SH', '000970.SZ', '300024.SZ', '600009.SH', '601318.SH',
                 '002120.SZ', '000538.SZ', '002372.SZ', '002601.SZ', '600597.SH', '600066.SH', '600406.SH', '002027.SZ',
                 '000776.SZ', '000002.SZ', '000878.SZ', '300124.SZ']

"""
获取上市公司股东人数，数据不定期公布
"""


def daily_check():
    # begin = '20190701'
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y%m%d")

    # 查看自选股北向资金持股数据和趋势
    for ts_code in MY_STOCK_LIST:
        hkholddata.analyze_hk_hold_data(ts_code, '20190701', yesterday, True)

    # 分析和汇总北向资金和南向资金数据和近日趋势
    hkholddata.analyze_moneyflow_hsgt_data('20200201', yesterday)
    hkholddata.analyze_moneyflow_hsgt_data('20200201', yesterday, isNorth=False)

    # 查看自选股资金流向数据
    for ts_code in MY_STOCK_LIST:
        dailydata.analyze_moneyflow(ts_code, '20200301', yesterday, True)

    # 查看自选股融资融券数据和趋势
    for ts_code in MY_STOCK_LIST:
        margintrading.analyze_margin_data_for_single_stock(ts_code, '20200201', yesterday, True)

    # 查看整个市场融资融券数据
    margintrading.analyze_margin_data_for_whole_market('20200201', yesterday, True)

    # 查看SHIBOR和美国国债利率数据
    ratedata.query_shibor('20200101', yesterday, True)
    ratedata.query_us_government_bonds_return_rate('20200101', yesterday, True)


if __name__ == '__main__':
    daily_check()