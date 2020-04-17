# -*- coding:UTF-8 -*-
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import time

"""
Class Description:
    financedata.py
    
Author:
    Ivan Ai
Created:
    2020/2/22
"""

ts.set_token('7c4d85f2c6728eb1bee17c7de4bfc61bc0a845fb62f9c8e8d3a84bcd')
pro = ts.pro_api()

pd.set_option('display.column_space', 100)
pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.width', 1000)

# 加这个两句 可以显示中文
plt.rcParams['font.sans-serif'] = ['STFangsong']
plt.rcParams['axes.unicode_minus'] = False

# 查询当前所有正常上市交易的股票列表，获取代码和名称对应表
# 将此调用放到全局变量，减少循环中调用tushre接口的次数
all_stock_data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,name')

"""
获取单一上市公司利润表数据
如果提供了报告期参数period，返回当报告期的数据
否则返回从公告开始日期start_date到公告结束日期end_date所有报告的数据
"""


def query_profit_data(ts_code, start_date, end_date, period='000000'):
    fields = 'ts_code, end_date, report_type, basic_eps, total_revenue, revenue, total_cogs, ' \
             'sell_exp, admin_exp, fin_exp, operate_profit, n_income, ebitda, report_type, update_flag'
    if period == '000000':
        result = pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date, fields=fields)
    else:
        result = pro.income(ts_code=ts_code, period=period, fields=fields)

    result.drop_duplicates(['end_date', 'report_type'], keep='last', inplace=True)

    # 删除比开始时间早的数据，start_date为20170101的时候，我们可能会取到20161231的数据，需要去掉
    tbd_list = []
    for index, row in result.iterrows():
        if time.strptime(row['end_date'], "%Y%m%d") < time.strptime(start_date, "%Y%m%d"):
            tbd_list.append(index)
    result.drop(tbd_list, inplace=True)

    # 添加股票名称信息
    result = result.join(all_stock_data.set_index('ts_code'), on='ts_code')

    result.sort_values(by='end_date', ascending=True, inplace=True)
    result.reset_index(drop=True, inplace=True)

    return result


"""
以表格和图分析和展示利润表数据
"""


def analyze_profit_data(ts_code, start_date, end_date, plot=False):
    result = query_profit_data(ts_code, start_date, end_date)

    # 打印利润表数据
    print(result)

    s_revenue = result['revenue']
    s_revenue.replace([None], 0, inplace=True)
    s_revenue = s_revenue.pct_change(periods=4)
    s_revenue.fillna(0, inplace=True)

    s_total_cogs = result['total_cogs']
    s_total_cogs.replace([None], 0, inplace=True)
    s_total_cogs = s_total_cogs.pct_change(periods=4)
    s_total_cogs.fillna(0, inplace=True)

    s_sell_exp = result['sell_exp']
    s_sell_exp.replace([None], 0, inplace=True)
    s_sell_exp = s_sell_exp.pct_change(periods=4)
    s_sell_exp.fillna(0, inplace=True)

    s_admin_exp = result['admin_exp']
    s_admin_exp.replace([None], 0, inplace=True)
    s_admin_exp = s_admin_exp.pct_change(periods=4)
    s_admin_exp.fillna(0, inplace=True)

    s_fin_exp = result['fin_exp']
    s_fin_exp.replace([None], 0, inplace=True)
    s_fin_exp = s_fin_exp.pct_change(periods=4)
    s_fin_exp.fillna(0, inplace=True)

    s_operate_profit = result['operate_profit']
    s_operate_profit.replace([None], 0, inplace=True)
    s_operate_profit = s_operate_profit.pct_change(periods=4)
    s_operate_profit.fillna(0, inplace=True)

    # 格式化打印同比数据
    s_end_date = result['end_date']
    print("==" * 20 + " Year on Year data" + "==" * 20)
    print(
        'report date' + '\t\t\t' + 'revenue' + '\t\t\t' + 'total_costs' + '\t\t' + 'sell_exp' + '\t\t' + 'admin_exp' + '\t\t' + 'fin_exp' + '\t\t' + 'operate_profit')
    for key, value in s_end_date.items():
        print(value + '\t\t\t' + '{:.2f}%'.format(s_revenue.get(key) * 100) + '\t\t\t' + '{:.2f}%'.format(
            s_total_cogs.get(key) * 100) + '\t\t\t' + '{:.2f}%'.format(
            s_sell_exp.get(key) * 100) + '\t\t\t' + '{:.2f}%'.format(
            s_admin_exp.get(key) * 100) + '\t\t\t' + '{:.2f}%'.format(
            s_fin_exp.get(key) * 100) + '\t\t\t' + '{:.2f}%'.format(s_operate_profit.get(key) * 100))

    # 画图展示
    if plot:
        ax1 = result.plot.bar(x='end_date',
                              y=['revenue', 'total_cogs', 'sell_exp', 'admin_exp', 'fin_exp', 'operate_profit'],
                              figsize=(15, 7))
        ax1.set_xlabel("")

        ax2 = ax1.twinx()
        ax2.plot(s_revenue, label='revenue YoY')
        ax2.plot(s_total_cogs, label='total_cogs YoY')
        ax2.plot(s_sell_exp, label='sell_exp YoY')
        ax2.plot(s_admin_exp, label='admin_exp YoY')
        ax2.plot(s_fin_exp, label='fin_exp YoY')
        ax2.plot(s_operate_profit, label='operate_profit YoY')

        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        plt.title(
            "个股主要利润表数据图 - " + result.at[1, 'ts_code'] + " (" + result.at[0, 'name'] + ") ")
        plt.show()


"""
根据利润表收入增长率选择股票
暂时判断的标准为最近3年12个报告期的revenue平均增长率大于10%
"""


def choose_stock_by_revenue_growth(lst_stock, start_date, end_date):
    ret = list()

    run_num = 0
    last_invoke_time = time.time()

    for ts_code in lst_stock:
        # 该tushare接口每分钟最多访问60次，保险起见，当1分钟内调用次数超过50次就sleep（60秒）
        if run_num >= 50:
            current_time = time.time()
            if current_time - last_invoke_time <= 60:
                time.sleep(60)
                run_num = 0
                last_invoke_time = current_time

        result = query_profit_data(ts_code, start_date, end_date)
        run_num += 1

        # 打印利润表数据
        # print(result)

        s_revenue = result['revenue']
        s_revenue.replace([None], 0, inplace=True)
        s_revenue = s_revenue.pct_change(periods=4)
        s_revenue.fillna(0, inplace=True)

        # 获取最近3年，12个报告期的revenue同比增长序列，取平均值
        if len(s_revenue) > 12:
            three_s_revenue = s_revenue.tail(12)
            two_s_revenue = s_revenue.tail(8)
            one_s_revenue = s_revenue.tail(4)
            if 0.10 < three_s_revenue.mean() < two_s_revenue.mean() < one_s_revenue.mean():
                ret.append(ts_code)
                print(ts_code, result.at[0, 'name'])

    return ret


if __name__ == '__main__':
    # stock_list = all_stock_data['ts_code'].tolist()
    # stock_list = ['601328.SH', '000898.SZ', '002004.SZ', '300024.SZ', '600835.SH', '600009.SH', '600519.SH', '601318.SH', '002236.SZ']
    # stock_list = ['002415.SZ']

    # lst_result = choose_stock_by_revenue_growth(stock_list, '20150101', '20191231')
    # print(lst_result)

    stock_list = ['601328.SH', '000898.SZ', '600835.SH', '000538.SZ', '600009.SH', '601318.SH', '002120.SZ',
                  '002372.SZ', '300024.SZ', '600597.SH', '601877.SH', '600066.SH', '600406.SH', '002027.SZ',
                  '600498.SH']
    for ts_code in stock_list:
        analyze_profit_data(ts_code, '20150101', '20191231', True)

    # stock_list = ['000008.SZ', '000088.SZ', '000401.SZ', '000507.SZ', '000596.SZ', '000656.SZ', '000682.SZ',
    #               '000686.SZ', '000708.SZ', '000912.SZ', '000930.SZ', '000931.SZ', '000966.SZ', '000967.SZ',
    #               '001965.SZ', '002028.SZ', '002049.SZ', '002081.SZ', '002088.SZ', '002100.SZ', '002124.SZ',
    #               '002152.SZ', '002179.SZ', '002189.SZ', '002191.SZ', '002202.SZ', '002214.SZ', '002250.SZ',
    #               '002254.SZ', '002262.SZ', '002267.SZ', '002299.SZ', '002313.SZ', '002353.SZ', '002382.SZ',
    #               '002386.SZ', '002444.SZ', '002458.SZ', '002463.SZ', '002520.SZ', '002531.SZ', '002541.SZ',
    #               '002555.SZ', '002563.SZ', '002594.SZ', '002595.SZ', '002653.SZ', '002690.SZ', '002698.SZ',
    #               '002726.SZ', '002745.SZ', '002746.SZ', '002791.SZ', '002812.SZ', '002821.SZ', '002851.SZ',
    #               '002869.SZ', '002876.SZ', '002901.SZ', '002916.SZ', '300034.SZ', '300078.SZ', '300130.SZ',
    #               '300132.SZ', '300142.SZ', '300149.SZ', '300209.SZ', '300259.SZ', '300292.SZ', '300352.SZ',
    #               '300384.SZ', '300417.SZ', '300424.SZ', '300428.SZ', '300474.SZ', '300487.SZ', '300529.SZ',
    #               '300558.SZ', '300567.SZ', '300570.SZ', '300572.SZ', '300579.SZ', '300682.SZ', '300702.SZ',
    #               '300709.SZ', '300726.SZ', '300735.SZ', '300737.SZ', '300750.SZ']
    # stock_list = ['600009.SH', '600025.SH', '600048.SH', '600129.SH', '600161.SH', '600170.SH', '600185.SH',
    #               '600206.SH', '600276.SH', '600332.SH', '600378.SH', '600383.SH', '600388.SH', '600428.SH',
    #               '600580.SH', '600585.SH', '600655.SH', '600673.SH', '600795.SH', '600811.SH', '600820.SH',
    #               '600837.SH', '600845.SH', '600985.SH', '600999.SH', '601012.SH', '601233.SH', '601369.SH',
    #               '601377.SH', '601607.SH', '601611.SH', '601615.SH', '601618.SH', '601668.SH', '601688.SH',
    #               '601872.SH', '601899.SH', '601952.SH', '603218.SH', '603259.SH', '603345.SH', '603360.SH',
    #               '603368.SH', '603508.SH', '603520.SH', '603605.SH', '603690.SH', '603713.SH', '603737.SH',
    #               '603803.SH', '603806.SH', '603881.SH', '603939.SH']
    #
    # for ts_code in stock_list:
    #     analyze_profit_data(ts_code, '20150101', '20191231', True)