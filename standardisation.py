import datetime
import pandas as pd
import threading  # Library for divide run time
import multiprocessing
from multiprocessing import Process
from threading import Thread
import time
import queue


# 146h on T2


def get_correct_date(day, month, hour, minutes, dataframe):
    in_period_entry = []
    just_after_period_entry = []
    max_index_found = dict()
    row_year = 0
    for index, row in dataframe.iterrows():
        if row_year != row['date_time'].year:
            index_after_trouve = False
            row_year = row['date_time'].year
        if datetime.datetime(row_year, month, day, hour, minutes, 0) <= row['date_time']:
            if (row['date_time']-datetime.datetime(row['date_time'].year, month, day, hour, minutes, 0)) < datetime.timedelta(minutes=30):
                in_period_entry.append(
                    {'date_time': row['date_time'], 'kwh': row['kwh']})
                max_index_found[row_year] = index
            elif not index_after_trouve:
                just_after_period_entry.append(
                    {'date_time': row['date_time'], 'kwh': row['kwh']})
                index_after_trouve = True
    return in_period_entry, just_after_period_entry, max_index_found


# 1:30s on T2
def get_correct_date_optimized(start_year, end_year, day, month, hour, minutes, dataframe):
    in_period_entry = []
    just_after_period_entry = []
    max_index_found = dict()
    for year in range(start_year, end_year+1):
        start_date = datetime.datetime(year, month, day, hour, minutes)
        end_date = start_date + datetime.timedelta(minutes=30)
        subset = dataframe[(dataframe.date_time >= start_date)
                           & (dataframe.date_time < end_date)]
        for index, row in subset.iterrows():
            in_period_entry.append(
                {'date_time': row['date_time'], 'kwh': row['kwh']})
            max_index_found[year] = index
        subset = dataframe[(dataframe.date_time >= end_date)]
        if not subset.empty:
            just_after_period_entry.append(
                {'date_time': subset['date_time'].iloc[0], 'kwh': subset['kwh'].iloc[0]})
    return in_period_entry, just_after_period_entry, max_index_found


def calcul_period_consumption(start_year, end_year, day, month, hour, minutes, dataframe, previous_empty_periods_comsumption):
    in_period_entry, just_after_period_entry, max_index_found = get_correct_date_optimized(
        start_year, end_year, day, month, hour, minutes, dataframe)
    if len(in_period_entry) == 0:
        consumption = 0.0
        if len(just_after_period_entry) > 0:
            for values in just_after_period_entry:
                entry_date = datetime.datetime(
                    values['date_time'].year, month, day, hour, minutes)
                previous_consumption_on_period = previous_empty_periods_comsumption / \
                    len(just_after_period_entry)
                consumption += (values['kwh']-previous_consumption_on_period)/(
                    (values['date_time']-entry_date).total_seconds()/60)*30.0
            previous_empty_periods_comsumption += consumption / \
                len(just_after_period_entry)
            period_consumption = round(abs(consumption /
                                           len(just_after_period_entry)), 5)
        else:
            period_consumption = 0
    else:
        consumption = -previous_empty_periods_comsumption
        for values in in_period_entry:
            consumption += values['kwh']
        period_consumption = round(abs(consumption /
                                       (len(max_index_found))), 5)
        previous_empty_periods_comsumption = 0.0
    return period_consumption, previous_empty_periods_comsumption


def standardisation_one_year_thirty_minutes(dataframe, df_result):
    first_date = dataframe['date_time'][dataframe.index[0]]
    last_date = dataframe['date_time'][dataframe.index[-1]]
    start_year = first_date.year
    end_year = last_date.year
    number_days = (dataframe['date_time'][dataframe.index[-1]] -
                   dataframe['date_time'][dataframe.index[0]]).days + 1
    previous_empty_periods_comsumption = 0.0
    for index, row in df_result.iterrows():
        # start_index_iteration = datetime.datetime.now()
        day = row['date_time'].day
        month = row['date_time'].month
        year = row['date_time'].year
        hour = row['date_time'].hour
        minutes = row['date_time'].minute
        if number_days < 365:
            if (first_date.month > last_date.month):
                if datetime.datetime(year, month, day, hour, minutes) <= datetime.datetime(year, last_date.month, last_date.day, last_date.hour, last_date.minute):
                    df_result.loc[index, 'kwh'], previous_empty_periods_comsumption = calcul_period_consumption(
                        start_year, end_year, day, month, hour, minutes, dataframe, previous_empty_periods_comsumption)
                elif datetime.datetime(year, month, day, hour, minutes) < datetime.datetime(year, first_date.month, first_date.day, first_date.hour, first_date.minute):
                    df_result.loc[index, 'kwh'] = 0
                else:
                    df_result.loc[index, 'kwh'], previous_empty_periods_comsumption = calcul_period_consumption(
                        start_year, end_year, day, month, hour, minutes, dataframe, previous_empty_periods_comsumption)
            else:
                if datetime.datetime(year, month, day, hour, minutes) < datetime.datetime(year, first_date.month, first_date.day, first_date.hour, first_date.minute):
                    df_result.loc[index, 'kwh'] = 0
                elif datetime.datetime(year, month, day, hour, minutes) <= datetime.datetime(year, last_date.month, last_date.day, last_date.hour, last_date.minute):
                    df_result.loc[index, 'kwh'], previous_empty_periods_comsumption = calcul_period_consumption(
                        start_year, end_year, day, month, hour, minutes, dataframe, previous_empty_periods_comsumption)
                else:
                    df_result.loc[index, 'kwh'] = 0
        else:
            df_result.loc[index, 'kwh'], previous_empty_periods_comsumption = calcul_period_consumption(
                start_year, end_year, day, month, hour, minutes, dataframe, previous_empty_periods_comsumption)
    return df_result


def standardisation_one_year_thirty_minutes_multi_threading(dataframe, df_result):
    x = len(df_result)
    recovery = 96
    step = recovery*183
    df_mt_result = pd.DataFrame(columns=['date_time', 'kwh'])
    if x < step:
        df_mt_result = standardisation_one_year_thirty_minutes(
            dataframe, df_result)
    else:
        try:
            que = queue.Queue()
            threads_list = list()
            y = step
            t = Thread(target=lambda q, arg1, arg2: q.put(standardisation_one_year_thirty_minutes(
                arg1, arg2)), args=(que, dataframe, df_result[:y].copy()), daemon=True)
            t.start()
            threads_list.append(t)
            while y < x-step:
                t = Thread(target=lambda q, arg1, arg2: q.put(standardisation_one_year_thirty_minutes(
                    arg1, arg2)), args=(que, dataframe, df_result[y-2*recovery:y+step].copy()), daemon=True)
                y += step
                t.start()
                threads_list.append(t)
            t = Thread(target=lambda q, arg1, arg2: q.put(standardisation_one_year_thirty_minutes(
                arg1, arg2)), args=(que, dataframe, df_result[y-2*recovery:].copy()), daemon=True)
            t.start()
            threads_list.append(t)
            for t in threads_list:
                t.join()
            while not que.empty():
                df_mt = que.get()
                if len(df_mt) == step:
                    df_mt_result = df_mt_result.append(df_mt[0:step-recovery])
                elif len(df_mt) == (x-y+2*recovery):
                    df_mt_result = df_mt_result.append(df_mt[recovery:])
                else:
                    df_mt_result = df_mt_result.append(
                        df_mt[recovery:step+recovery])
            df_mt_result.sort_values(by=['date_time'], inplace=True)
            df_mt_result.reset_index(inplace=True, drop=True)
        except:
            print("Issue in multithreaded conversion")

    return df_mt_result


def standardisation_one_year_thirty_minutes_for_mp(dataframe, df_result, i, return_dict):
    return_dict[i] = standardisation_one_year_thirty_minutes(
        dataframe, df_result)


def standardisation_one_year_thirty_minutes_multi_processing(dataframe, df_result):
    x = len(df_result)
    recovery = 24
    step = recovery*183
    df_mt_result = pd.DataFrame(columns=['date_time', 'kwh'])
    if x < step:
        df_mt_result = standardisation_one_year_thirty_minutes(
            dataframe, df_result)
    else:
        # try:
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        process_list = list()
        y = step
        p = Process(target=standardisation_one_year_thirty_minutes_for_mp, args=(
            dataframe, df_result[:y].copy(), len(process_list), return_dict))
        p.start()
        process_list.append(p)
        while y < x-step:
            p = Process(target=standardisation_one_year_thirty_minutes_for_mp, args=(
                dataframe, df_result[y-2*recovery:y+step].copy(), len(process_list), return_dict))
            y += step
            p.start()
            process_list.append(p)
        p = Process(target=standardisation_one_year_thirty_minutes_for_mp, args=(
            dataframe, df_result[y-2*recovery:].copy(), len(process_list), return_dict))
        p.start()
        process_list.append(p)
        for p in process_list:
            p.join()
        for i in range(0, len(process_list)):
            df_mt = return_dict[i]
            if len(df_mt) == step:
                df_mt_result = df_mt_result.append(df_mt[0:step-recovery])
            elif len(df_mt) == (x-y+2*recovery):
                df_mt_result = df_mt_result.append(df_mt[recovery:])
            else:
                df_mt_result = df_mt_result.append(
                    df_mt[recovery:step+recovery])
        df_mt_result.sort_values(by=['date_time'], inplace=True)
        df_mt_result.reset_index(inplace=True, drop=True)
        # except:
        #    print("Issue in multiprocessing conversion for standardisation")

    return df_mt_result
