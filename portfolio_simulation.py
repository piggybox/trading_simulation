# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys


def main():
    cash, order_file = sys.argv[1:]
    start, end, symbols, orders = parse_order(order_file)
    quotes = retrieve_quotes(start, end, symbols)
    portfolio_performance = trace_portfolio(quotes, orders, int(cash))

    # for x in portfolio_performance:
    #     print x

    summarize_performance(portfolio_performance, int(cash))


def parse_order(order_file):
    tmp = np.loadtxt(order_file, dtype='str', delimiter=',')
    # convert date
    orders = [[dt.datetime(int(row[0]),int(row[1]),int(row[2]), 16), row[3], row[4], int(row[5])] for row in tmp]
    orders.sort()  # sort order by date, very important

    start = orders[0][0]
    end = orders[-1][0]
    symbols = np.unique([row[1] for row in orders])
    return start, end, symbols, orders


def retrieve_quotes(start, end, symbols):
    # retrieve data
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start, end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    #check and wash
    df_rets = d_data['close'].copy()
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    return df_rets


def trace_portfolio(quotes, orders, cash):
    #mash them up!
    portfolio = []
    order_id = 0
    symbols = quotes.columns  # stocks

    for i in range(quotes.index.size):  # 0 .. len-1
        # portfolio daily summay: date, quotes, shares, cash, total
        date = quotes.index[i]
        daily = [date, quotes.values[i]]

        if i == 0:
            # initialize all shares to 0
            zero_shares = np.zeros(len(symbols), dtype=np.int)
            daily.append(zero_shares)
            daily.append(cash)
        else:
            daily.append(portfolio[i - 1][2])  # same shares as yesterday
            daily.append(portfolio[i - 1][3])  # same cash as yesterday

        # multiple transactions can happen in the same day
        while order_id < len(orders) and date == orders[order_id][0]:  # 0 order date
            stock_name = orders[order_id][1]
            stock_id = symbols.indexMap[stock_name]  # used in daily[2]
            action = orders[order_id][2]
            shares = orders[order_id][3]
            price = quotes[stock_name][i]

            if action == 'Buy':
                daily[2][stock_id] = daily[2][stock_id] + shares  # update shares
                daily[3] = daily[3] - price * shares  # update cash

            if action == 'Sell':
                daily[2][stock_id] = daily[2][stock_id] - shares  # update shares
                daily[3] = daily[3] + price * shares  # update cash

            order_id = order_id + 1  # move to the next order

        # update total on daily basis no matter a transaction happened or not
        daily.append(np.sum(daily[1] * daily[2]) + daily[3])  # quotes * share + cash

        # trick to solve a bug zerofying the share array
        if type(daily[2]) is np.ndarray:
            daily[2] = daily[2].copy()

        portfolio.append(daily)

    return portfolio


def summarize_performance(portfolio_performance, cash):
    # calcualte return and sharp ratio
    daily_total = [x[4] for x in portfolio_performance]  # daily total copy?

    cumulative_return = (daily_total[-1]/cash - 1)*100
    print "total return: " + str(cumulative_return) + '%'

    #na_normalized_price = na_price / na_price[0, :]
    daily_total = np.array(daily_total)  # need numpy array for tsu
    tsu.returnize0(daily_total)   # daily return

    std = np.std(daily_total)  # SD of daily return
    print "std:" + str(std)

    mean = np.average(daily_total)  # Average portfolio daily return
    print "mean:" + str(mean)

    # Sharp ratio
    sharpe_ratio = 252**(0.5) * (mean / std)
    print "sharp ratio: " + str(sharpe_ratio)

if __name__ == '__main__':
    main()

