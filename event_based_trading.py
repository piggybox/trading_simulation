
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    f = open('orders.csv', 'w')
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yesterday = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            #f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            #f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            #f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            #f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            if f_symprice_yesterday >= 8.0 and f_symprice_today < 8.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

                f.write(ldt_timestamps[i].strftime('%Y,%m,%d,') + s_sym + ',Buy,100,\n')
                if (i + 5) <= (len(ldt_timestamps) - 1):
                    f.write(ldt_timestamps[i + 5].strftime('%Y,%m,%d,') + s_sym + ',Sell,100,\n')
                else:
                    f.write(ldt_timestamps[-1].strftime('%Y,%m,%d,') + s_sym + ',Sell,100,\n')

    f.close()
    #return df_events

# generate_order(events):
    # order strategy and output to order.csv


if __name__ == '__main__':
    # Group 1
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # actually should fill any missing data, not just closing price
    d_data['actual_close'] = d_data['actual_close'].fillna(method='ffill')
    d_data['actual_close'] = d_data['actual_close'].fillna(method='bfill')
    d_data['actual_close'] = d_data['actual_close'].fillna(1.0)  # ?

    print "Finding Events"
    find_events(ls_symbols, d_data)

    # ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
    #     s_filename='2012-6.pdf', b_market_neutral=True, b_errorbars=True,
    #     s_market_sym='SPY')
