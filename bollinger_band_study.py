# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    ts_market = d_data['SPY']

    # Creating an empty dataframe
    df_events = copy.deepcopy(d_data)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = d_data.index  # -20?

    f = open('orders.csv', 'w')
    for s_sym in ls_symbols:
        for i in range(20, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            bollinger_today = d_data[s_sym].ix[ldt_timestamps[i]]
            bollinger_yesterday = d_data[s_sym].ix[ldt_timestamps[i - 1]]
            market_bollinger_today = ts_market.ix[ldt_timestamps[i]]
            #f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            #f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            #f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            if bollinger_yesterday >= -2.0 and bollinger_today < -2.0 and market_bollinger_today >= 1.2:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

                f.write(ldt_timestamps[i].strftime('%Y,%m,%d,') + s_sym + ',Buy,100,\n')
                if (i + 5) <= (len(ldt_timestamps) - 1):
                    f.write(ldt_timestamps[i + 5].strftime('%Y,%m,%d,') + s_sym + ',Sell,100,\n')
                else:
                    f.write(ldt_timestamps[-1].strftime('%Y,%m,%d,') + s_sym + ',Sell,100,\n')

    f.close()
    # return df_events


if __name__ == '__main__':
    symbols = ["MSFT", "SPY"]
    startday = dt.datetime(2008, 1, 1)
    endday = dt.datetime(2009, 12, 31)
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startday, endday, timeofday)
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    adjcloses = d_data['close'].fillna(method='ffill')
    adjcloses = d_data['close'].fillna(method='bfill')

    means = pd.rolling_mean(adjcloses, 20, min_periods=20)
    std = pd.rolling_std(adjcloses, 20, min_periods=20)
    bollinger_band = (adjcloses - means)/std

    print "Finding Events"
    find_events(ls_symbols, bollinger_band)

    # print df_events
    # ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
    #     s_filename='bollinger_band.pdf', b_market_neutral=True, b_errorbars=True,
    #     s_market_sym='SPY')



    # for i in range(bollinger_band.index.size):
    #     print str(bollinger_band.index[i]) + " " + str(bollinger_band.values[i])
