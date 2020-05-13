import pandas as pd  # Library for treating DATA
import numpy as np
import datetime  # Library for treating TIME
import sys
import multiprocessing
from multiprocessing import Process
import threading  # Library for divide run time
from threading import Thread
import time
import queue


# ----------------------------------------------------------------------------
# First way: Convert kilo-watts to kilo-watt-hour

def suppression_zero_value_initial_final(df):
    x = len(df)
    i = 0
    j = x-1
    for index, row in df.iterrows():
        if (row['kwh'] == '' or row['kwh'] == 0) and index == i:
            i += 1
        if (df['kwh'][x-1-index] == '' or df['kwh'][x-1-index] == 0) and (x-1-index == j):
            j -= 1
        if (i != index and j != x-1-index) or i > j:
            break
    return df[i:j+1]


def kW_kWh(df):

    # Create a Dataframe with two columns "date_time" and "kwh"
    df_result = pd.DataFrame(columns=['date_time', 'kwh'])
    for index, row in df.iterrows():
        # datetime ???
        if index == 0:
            dt = (df['date_time'][index+1] -
                  df['date_time'][index]).total_seconds() / 3600
        elif index == len(df)-1:
            dt = (df['date_time'][index]-df['date_time']
                  [index-1]).total_seconds() / 3600
        else:
            dt = ((df['date_time'][index+1]-df['date_time']
                   [index-1]).total_seconds() / 3600)/2
        dict_1 = {}
        dict_1['date_time'] = df['date_time'][index]
        dict_1['kwh'] = df['kW'][index]*dt
        df_result = df_result.append(dict_1, ignore_index=True)

    # convert resault(int) to FLOAT
    df_result['kwh'] = df_result['kwh'].astype(float)

    return df_result

# ----------------------------------------------------------------------------
# Second way: Convert kilo-watts to kilo-watt-hour (reduce run time)


def kW_kWh_optimized(df):
    df.reset_index(inplace=True)
    df_result = pd.DataFrame(columns=['date_time', 'kwh'])
    x = len(df)
    if x > 1:
        d = dict()
        for i in range(x):
            l = [0] * x
            if x == 2:
                if i == 0:
                    l[0] = -1/3600
                    l[1] = -1/3600
                else:
                    l[0] = 1/3600
                    l[1] = 1/3600
            elif x == 3:
                if i == 0:
                    l[0] = -1/3600
                    l[1] = -0.5/3600
                elif i == x-1:
                    l[x-2] = 0.5/3600
                    l[x-1] = 1/3600
                else:
                    l[i-1] = 1/3600
                    l[i+1] = -1/3600
            else:
                if i == 0:
                    l[0] = -1/3600
                    l[1] = -0.5/3600
                if i == 1:
                    l[0] = 1/3600
                    l[2] = -0.5/3600
                elif i == x-2:
                    l[x-3] = 0.5/3600
                    l[x-1] = -1/3600
                elif i == x-1:
                    l[x-2] = 0.5/3600
                    l[x-1] = 1/3600
                else:
                    l[i-1] = 1/(2*3600)
                    l[i+1] = -1/(2*3600)
            d[i] = l
        dmultiply = pd.DataFrame(data=d)
    else:
        dmultiply = pd.DataFrame(data={'0': [1]})
    df_result['date_time'] = df['date_time']
    df_result['kwh'] = dmultiply.dot(
        df['date_time'].apply(lambda x: x.timestamp()))*df['kW']
    return df_result


def kW_kWh_optimized_for_mp(df, i, return_dict):  # mp = Multiprocessing
    return_dict[i] = kW_kWh_optimized(df)

# ----------------------------------------------------------------------------
# Threading DATA for get result faster


def kW_kWh_multi_threaded(df):
    df_result = pd.DataFrame(columns=['date_time', 'kwh'])
    x = len(df)
    recovery = 1
    step = recovery*250
    if x < step:
        df_result = kW_kWh_optimized(df)
    else:
        try:
            que = queue.Queue()
            threads_list = list()
            y = step
            t = Thread(target=lambda q, arg: q.put(kW_kWh_optimized(
                arg)), args=(que, df[:y]), daemon=True)
            t.start()
            threads_list.append(t)
            while y < x-step:
                t = Thread(target=lambda q, arg: q.put(kW_kWh_optimized(
                    arg)), args=(que, df[y-2*recovery:y+step]), daemon=True)
                y += step
                t.start()
                threads_list.append(t)
            t = Thread(target=lambda q, arg: q.put(kW_kWh_optimized(
                arg)), args=(que, df[y-2*recovery:]), daemon=True)
            t.start()
            for t in threads_list:
                t.join()
            while not que.empty():
                df_mt = que.get()
                if len(df_mt) == step:
                    df_result = df_result.append(df_mt[0:step-recovery])
                elif len(df_mt) == (x-y+2*recovery):
                    df_result = df_result.append(df_mt[recovery:])
                else:
                    df_result = df_result.append(
                        df_mt[recovery:step+recovery])
            df_result.sort_values(by=['date_time'], inplace=True)
            df_result.reset_index(inplace=True, drop=True)
        except:
            print("Issue in multithreaded conversion")
    return df_result


def kW_kWh_multi_processed(df):
    df_result = pd.DataFrame(columns=['date_time', 'kwh'])
    x = len(df)
    recovery = 1
    step = recovery*250
    if x < step:
        df_result = kW_kWh_optimized(df)
    else:
        try:
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            process_list = list()
            y = step
            p = Process(target=kW_kWh_optimized_for_mp, args=(
                df[:y], len(process_list), return_dict))
            p.start()
            process_list.append(p)
            while y < x-step:
                p = Process(target=kW_kWh_optimized_for_mp, args=(
                    df[y-2*recovery:y+step], len(process_list), return_dict))
                y += step
                p.start()
                process_list.append(p)
            p = Process(target=kW_kWh_optimized_for_mp, args=(
                df[y-2*recovery:], len(process_list), return_dict))
            p.start()
            process_list.append(p)
            for p in process_list:
                p.join()
            for i in range(0, len(process_list)):
                df_mt = return_dict[i]
                if len(df_mt) == step:
                    df_result = df_result.append(df_mt[0:step-recovery])
                elif len(df_mt) == (x-y+2*recovery):
                    df_result = df_result.append(df_mt[recovery:])
                else:
                    df_result = df_result.append(
                        df_mt[recovery:step+recovery])
            df_result.sort_values(by=['date_time'], inplace=True)
            df_result.reset_index(inplace=True, drop=True)
        except:
            print("Issue in multiprocessing conversion for normalisation")
    return df_result

# ----------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


dispatch = {
    "web": kW_kWh_multi_threaded,
    "standalone": kW_kWh_multi_processed,
}


def template1(csv, origin="standalone"):
    ''' The function that return Template_1 with good format (T1_csv_1h) '''

    start_date = datetime.datetime.now()

    df = pd.read_csv(csv, sep='delimiter', engine='python')
    new = df['datetime;W'].str.split('(;| )', n=2, expand=True)
    df['date_time'] = new[0]
    df['Watts'] = new[2]
    df['date_time'] = pd.to_datetime(
        df['date_time'], format='%Y%m%d:%H%M', errors='ignore')
    df['Watts'] = df['Watts'].str.replace(',', '.').astype(float)
    get_kW = df.select_dtypes(exclude=['object', 'datetime']) * 0.001
    df['kW'] = get_kW['Watts']  # rename col Watt to kW

    end_prep_date = datetime.datetime.now()

    try:
        function = dispatch[origin]
    except KeyError:
        function = kW_kWh_multi_threaded

    return "Template 1", end_prep_date-start_date, function(df)


# ----------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


def template2(csv, origin="standalone"):
    ''' The function that return Template_2 with good format (T2_csv_10min) '''

    start_date = datetime.datetime.now()

    df = pd.read_csv(csv, sep='delimiter', engine='python')
    new = df['Date;Time;W'].str.split('([^;]*;[^;]*;)', n=2, expand=True)
    df["date_time"] = new[1]
    df['Watts'] = new[2]
    df["date_time"] = pd.to_datetime(
        df["date_time"], format='%d/%m/%Y;%H:%M;', errors='ignore')
    df['Watts'] = pd.to_numeric(df['Watts'], errors='coerce')
    df['Watts'] = df['Watts'].fillna(0)
    kW = df.select_dtypes(exclude=['object', 'datetime']) * 0.001
    df['kW'] = kW['Watts']

    end_prep_date = datetime.datetime.now()

    try:
        function = dispatch[origin]
    except KeyError:
        function = kW_kWh_multi_threaded

    return "Template 2", end_prep_date-start_date, function(df)

# -----------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


def template3(csv, origin="standalone"):
    ''' The function that return Template_3 with good format (T3_csv_10min) '''

    start_date = datetime.datetime.now()

    df = pd.read_csv(csv, sep='delimiter', engine='python')
    new = df['Datetime;W'].str.split(';', n=1, expand=True)
    df['date_time'] = new[0]
    df['Watts'] = new[1]
    df['date_time'] = pd.to_datetime(
        df['date_time'], format='%d/%m/%Y %H:%M', errors='ignore')
    df['Watts'] = pd.to_numeric(df['Watts'], errors='coerce')
    kW = df.select_dtypes(exclude=['object', 'datetime']) * 0.001
    df['kW'] = kW['Watts']

    end_prep_date = datetime.datetime.now()

    try:
        function = dispatch[origin]
    except KeyError:
        function = kW_kWh_multi_threaded

    return "Template 3", end_prep_date-start_date, function(df)

# ------------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


def template4(xlsx, origin="standalone"):
    ''' The function that return Template_4 with good format (T4_xlsx_5min) '''

    start_date = datetime.datetime.now()

    df = pd.read_excel(xlsx)
    df["date_time"] = df['Datetime']
    df["Watts"] = df['W']
    df["date_time"] = pd.to_datetime(
        df["date_time"], format='%d/%m/%Y %H:%M:%S', errors='ignore')
    kW = df.select_dtypes(exclude=['object', 'datetime']) * 0.001
    df['kW'] = kW['Watts']

    end_prep_date = datetime.datetime.now()

    try:
        function = dispatch[origin]
    except KeyError:
        function = kW_kWh_multi_threaded

    return "Template 4", end_prep_date-start_date, function(df)

# -------------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


def template5(csv, origin="standalone"):
    ''' The function that return Template_5 with good format (T5_csv_10min) '''

    start_date = datetime.datetime.now()

    df = pd.read_csv(csv, sep='delimiter', engine='python')
    new = df['Horodate;W'].str.split('([^]*;[^]*;)', n=2, expand=True)
    df['date_time'] = new[1]
    df['Watts'] = new[2]
    df['date_time'] = df['date_time'].str.replace("T", " ", case=False)
    df['date_time'] = df['date_time'].str.replace(";", "", case=False)
    df['date_time'] = pd.to_datetime(
        df['date_time'], format='%Y-%m-%d %H:%M:%S', errors='ignore', utc=True)
    df['date_time'] = df['date_time'].dt.tz_localize(None)
    df['Watts'] = df['Watts'].astype(float)
    df['Watts'] = df['Watts'].fillna(0)
    kW = df.select_dtypes(exclude=['object', 'datetime']) * 0.001
    df['kW'] = kW['Watts']

    end_prep_date = datetime.datetime.now()

    try:
        function = dispatch[origin]
    except KeyError:
        function = kW_kWh_multi_threaded

    return "Template 5", end_prep_date-start_date, function(df)

# ----------------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


def template6(xlsx, origin="standalone"):
    ''' The function that return Template_6 with good format (T6_xlsx_1h) '''

    start_date = datetime.datetime.now()

    df = pd.read_excel(xlsx)
    df['date_time'] = df['Datetime']
    df['date_time'] = df['date_time'].apply(lambda x: x.replace(microsecond=0))
    df['date_time'] = pd.to_datetime(df['date_time'], errors='ignore')
    df = df[['date_time', 'kW']]

    end_prep_date = datetime.datetime.now()

    try:
        function = dispatch[origin]
    except KeyError:
        function = kW_kWh_multi_threaded

    return "Template 6", end_prep_date-start_date, function(df)

# --------------------------------------------------------------------------------------


def template7(xlsx, origin="standalone"):
    ''' The function that return Template_7 with good format (T7_xlsx_1h) '''

    start_date = datetime.datetime.now()

    df = pd.read_excel(xlsx)

    df['date_time'] = df['Date'].str.cat(df['Time'], sep='')
    df.drop(columns=['Date', 'Time'], inplace=True)
    df['date_time'] = pd.to_datetime(df['date_time'], errors='ignore')
    df['kwh'] = df['kWh']
    df = df[['date_time', 'kwh']]

    end_prep_date = datetime.datetime.now()

    return "Template 7", end_prep_date-start_date, df

# ----------------------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


def template8(csv, origin="standalone"):
    ''' The function that return Template_8 with good format (T8_csv_30min) '''

    start_date = datetime.datetime.now()

    # convert csv to Dataframe
    df = pd.read_csv(csv, sep='delimiter', engine='python')
    df['Datetime;W;W'] = df['Datetime;W;W'].str.split(';')
    df[['date_time', 'Watts1', 'Watts2']] = pd.DataFrame(
        df['Datetime;W;W'].values.tolist(), index=df.index)
    df['date_time'] = pd.to_datetime(
        df['date_time'], format='%d/%m/%Y %H:%M', errors='ignore')
    df[['Watts1', 'Watts2']] = df[['Watts1', 'Watts2']].astype(float)
    get_kW = df.select_dtypes(exclude=['object', 'datetime']) * 0.001
    df[['kW1', 'kW2']] = get_kW[['Watts1', 'Watts2']]  # rename col Watt to kW
    df.sort_values(by=['date_time'], inplace=True)
    df.reset_index(inplace=True, drop=True)

    # df.to_csv("result_intermediaire_"+csv)
    df_result = pd.DataFrame(columns=['date_time', 'kW'])
    for index, row in df.iterrows():
        if index == len(df)-1:
            dt = (df['date_time'][index]-df['date_time'][index-1]) / 2
        else:
            dt = (df['date_time'][index+1]-df['date_time'][index]) / 2
        dict_1 = {}
        dict_2 = {}
        dict_1['date_time'] = df['date_time'][index]
        dict_1['kW'] = df['kW1'][index]
        df_result = df_result.append(dict_1, ignore_index=True)
        dict_2['date_time'] = df['date_time'][index] + \
            datetime.timedelta(dt.days, dt.seconds)
        dict_2['kW'] = df['kW2'][index]
        df_result = df_result.append(dict_2, ignore_index=True)

    end_prep_date = datetime.datetime.now()

    try:
        function = dispatch[origin]
    except KeyError:
        function = kW_kWh_multi_threaded

    return "Template 8", end_prep_date-start_date, function(df_result)

# ---------------------------------------------------------------------------
# first function for get col date-time and col w in datetime and kW(float)


def template9(csv, origin="standalone"):
    ''' The function that return Template_9 with good format (T9_csv_30min) '''

    start_date = datetime.datetime.now()

    # convert csv to Dataframe
    df = pd.read_csv(csv, sep='delimiter', engine='python')

    # split to 2 columns
    df['Horodate;Wh'] = df['Horodate;Wh'].str.split(';')

    # get 2 columns from primary column
    df[['date_time', 'Wh']] = pd.DataFrame(
        df['Horodate;Wh'].values.tolist(), index=df.index)

    # seperate date & time
    df['date_time'] = df['date_time'].str.replace(
        "T", " ", case=False)

    # remove time zone
    df['date_time'] = pd.to_datetime(
        df['date_time'], utc=True)
    df['date_time'] = df['date_time'].dt.tz_localize(None)

    # convert to float64
    df['Wh'] = df['Wh'].astype(float)

    # convert watt to kilowatts
    get_kW = df.select_dtypes(exclude=['object', 'datetime']) * 0.001

    # rename col Wh to kwh
    df['kwh'] = get_kW['Wh']

    # delete primary columns
    df.drop(columns=['Horodate;Wh', 'Wh'], inplace=True)

    # sort DATA from Jan to Dec
    df.sort_values(by=['date_time'], inplace=True)

    # replace and remove old index
    df.reset_index(inplace=True, drop=True)

    end_prep_date = datetime.datetime.now()

    return "Template 9", end_prep_date-start_date, df
