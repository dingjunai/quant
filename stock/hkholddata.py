# -*- coding:UTF-8 -*-
import tushare as ts
import matplotlib.pyplot as plt
import pandas as pd
import time
from datetime import date, timedelta
from stock import mytask

"""
Class Description:
    hkholddata.py
    
Author:
    Ivan Ai
Created:
    2019/11/25
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

"""
获取个股的沪深港通持股明细，并计算每日北向资金买入卖出量
合并个股每日开盘价，收盘价，最高价，最低价以及涨跌幅
返回合并信息的pandas dataframe格式以便分析北向资金买入卖出对个股的影响
"""


def query_hk_hold_data(ts_code, start_date, end_date):
    exchange = ts_code[-2:]
    # 获取沪深港通持股明细，数据来源于港交所
    data = pro.hk_hold(ts_code=ts_code, start_date=start_date, end_date=end_date, exchange=exchange)
    # print(data)

    # 获取交易所日历数据
    pd_trade_cal = pro.trade_cal(start_date=start_date, end_date=end_date)
    trade_cal_array = pd_trade_cal[pd_trade_cal['is_open'] == 1]['cal_date'].array
    # print(trade_cal_array)

    # 过滤掉沪深港通持股明细中非交易日行
    index_array_tbd = []
    for index, row in data.iterrows():
        if row['trade_date'] not in trade_cal_array:
            index_array_tbd.append(index)

    hk_hold_data = data.drop(index_array_tbd)
    hk_hold_data.reset_index(drop=True, inplace=True)
    # print(hk_hold_data)

    # 沪深港通在北向接口关闭但A股仍然交易的日期（比如'2019/05/13'和'2019/07/01'）不会返回数据，用前一个交易日的数据补回
    # 当天的北向持股数据第二天才会有，但交易数据当天晚上就有了，如果当天晚上运行程序也需要暂时用前一天的北向持股数据
    north_trade_cal_array = hk_hold_data['trade_date'].array
    n = 0
    while n < len(trade_cal_array):
        if trade_cal_array[n] not in north_trade_cal_array:
            trade_cal = trade_cal_array[n]
            pre_trade_cal = trade_cal_array[n - 1]
            pre_row_data = hk_hold_data[hk_hold_data['trade_date'] == pre_trade_cal]
            new_row_data = pre_row_data.copy()
            new_row_data['trade_date'] = trade_cal
            hk_hold_data = hk_hold_data.append(new_row_data, ignore_index=True)
        n += 1
    hk_hold_data.sort_values(by='trade_date', ascending=False, inplace=True)
    hk_hold_data.reset_index(drop=True, inplace=True)
    # print(hk_hold_data)

    # 计算北向资金delta，用前一天持仓数据减去当天持仓数据
    vol_array = hk_hold_data['vol'].array
    tmp_array = vol_array.copy()
    tmp_len = len(tmp_array)
    i = 0
    while i < tmp_len - 1:
        tmp_array[i] = tmp_array[i] - tmp_array[i + 1]
        i += 1
    if tmp_len > 0:
        tmp_array[tmp_len - 1] = 0
    vol_delta_series = pd.Series(tmp_array, name='vol_delta')

    # 获取日线行情
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    # print(df)

    result = pd.concat([hk_hold_data, vol_delta_series, df[['close', 'open', 'high', 'low', 'pct_chg']]], axis=1)
    result.sort_values(by='trade_date', ascending=True, inplace=True)
    result.drop(['exchange'], axis=1, inplace=True)
    result.reset_index(drop=True, inplace=True)

    return result


"""
以表格和图分析和展示北向资金持股和股价走势间的关系，默认输出最近20个交易日数据
"""


def analyze_hk_hold_data(ts_code, start_date, end_date, plot=False):
    result = query_hk_hold_data(ts_code, start_date, end_date)

    # 打印最近北向资金持股信息
    print(result.tail(25), "\n")

    # 画图展示北向资金持股比例和股价走势间的相关性
    if plot:
        ax = result.plot.line(x='trade_date', y=['ratio', 'close'], secondary_y=['close'], figsize=(15, 6))
        ax.set_xlabel("")
        plt.title(
            "北向资金持股比例和收盘价趋势图 - " + result.at[0, 'ts_code'] + " (" + result.at[0, 'name'] + ") ")
        plt.show()


"""
分析北向资金的加减仓趋势
"""


def query_hk_hold_data_trend(start_date, end_date, hs_type='SH', ratio_filter=2.0, plot=False):
    # 获取沪股通（hs_type='SH')或深股通(hs_type='SZ')成分股列表
    df = pro.hs_const(hs_type=hs_type)
    ts_code_series = df['ts_code']

    run_num = 0
    last_invoke_time = time.time()

    for index, val in ts_code_series.items():

        # 该tushare接口每分钟最多访问60次，保险起见，当1分钟内调用次数超过30次就sleep（60秒）
        if run_num >= 30:
            current_time = time.time()
            if current_time - last_invoke_time <= 60:
                time.sleep(60)
                run_num = 0
                last_invoke_time = current_time

        result = query_hk_hold_data(str(val), start_date, end_date)
        run_num += 1

        # 这里假设平均持股比例过小（由ratio_filter定义)的是被动配置，不在选择范围内
        if result['ratio'].mean() > ratio_filter:

            # 打印最近北向资金持股信息
            print(result.tail(20), "\n")

            # 画图展示北向资金持股比例和股价走势间的相关性
            if plot:
                result.plot.line(x='trade_date', y=['ratio', 'close'], secondary_y=['close'], figsize=(15, 5))
                plt.title(
                    "The figure of HK hold ratio and price of " + result.at[0, 'ts_code'] + " (" + result.at[
                        0, 'name'] + ") ")
                plt.show()

"""
获取沪深港通资金流向
"""


def query_moneyflow_hsgt_data(start_date, end_date):

    # 获取沪深港通资金流向，数据来源于港交所
    data = pro.moneyflow_hsgt(start_date=start_date, end_date=end_date)
    # print(data)

    return data


"""
以表格和图分析和展示获取沪深港通资金流向，默认输出最近20个交易日数据
"""


def analyze_moneyflow_hsgt_data(start_date, end_date, isNorth=True):
    result = query_moneyflow_hsgt_data(start_date, end_date)

    result.sort_values(by='trade_date', ascending=True, inplace=True)

    # 修改列名
    result.columns = ['trade_date', 'SHHK-Southbound', 'SZHK-Southbound', 'HKSH-Northbound', 'HKSZ-Northbound', 'Northbound', 'Southbound']

    # 打印最近北向资金持股信息
    print(result.tail(20), "\n")

    result_20 = result.tail(20)
    twenty_days_sum = result_20.sum(numeric_only=True)
    print("========== 20日数据汇总（单位：百万元） ==========")
    print(twenty_days_sum)

    result_10 = result.tail(10)
    ten_days_sum = result_10.sum(numeric_only=True)
    print("========== 10日数据汇总（单位：百万元） ==========")
    print(ten_days_sum)

    result_5 = result.tail(5)
    five_days_sum = result_5.sum(numeric_only=True)
    print("========== 5日数据汇总（单位：百万元） ==========")
    print(five_days_sum)

    # 画图展示获取沪深港通资金流向
    if isNorth:
        ax = result.plot.bar(x='trade_date', y=['HKSH-Northbound', 'HKSZ-Northbound', 'Northbound'], figsize=(15, 6))
        ax.set_xlabel("")
        plt.title("沪深港通资金流向 - 北向资金（单位：百万元）")
    else:
        ax = result.plot.bar(x='trade_date', y=['SHHK-Southbound', 'SZHK-Southbound', 'Southbound'], figsize=(15,6))
        ax.set_xlabel("")
        plt.title("沪深港通资金流向 - 南向资金（单位：百万元）")
    plt.show()


if __name__ == '__main__':
    begin = '20190701'
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y%m%d")

    # 查看自选股北向资金持股数据和趋势
    # stock_list = ['600036.SH', '002236.SZ']
    # stock_list = ['601328.SH', '000898.SZ', '600835.SH', '000538.SZ', '600009.SH', '601318.SH', '002120.SZ',
    #               '002372.SZ', '300024.SZ', '002601.SZ', '600597.SH', '601877.SH', '600066.SH', '600406.SH',
    #               '002027.SZ', '000776.SZ', '000002.SZ', '000878.SZ', '300124.SZ', '600498.SH', '600104.SH',
    #               '000651.SZ']
    for ts_code in mytask.MY_STOCK_LIST:
        analyze_hk_hold_data(ts_code, begin, yesterday, True)

    # 根据北向资金持股比例达到一定比例（这里是5.0)来条件选股
    # query_hk_hold_data_trend(begin, yesterday, 'SZ', 5.0,  True)

    # 分析和汇总北向资金和南向资金数据和近日趋势
    analyze_moneyflow_hsgt_data('20200201', yesterday)
    analyze_moneyflow_hsgt_data('20200201', yesterday, isNorth=False)
