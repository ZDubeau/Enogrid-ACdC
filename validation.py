import pandas as pd
import datetime


def kwh_on_normalize_df(df: pd.DataFrame):
    # for remove 29 February
    df = df.loc[~(df['date_time'].dt.month.eq(
        2) & df['date_time'].dt.day.eq(29))].copy()
    df.sort_values(by=['date_time'], inplace=True)
    df.reset_index(inplace=True, drop=True)
    start = df['date_time'][0]
    end = df['date_time'][len(df)-1]
    Total = 0
    # Calculate delta
    if start.year == end.year:
        Total += df['kwh'].sum()

    # Example 21/06/2016 - 01/02/2018
    elif end < datetime.datetime(year=end.year, month=start.month, day=start.day, hour=start.hour, minute=start.minute, second=start.second):

        # sum of kWh in period [01/JAN to 01/FEB] in 2017 and 2018 divide by 2
        for i in range(start.year+1, end.year+1):
            start_date = datetime.datetime(
                year=i, month=1, day=1, hour=0, minute=0, second=0)
            end_date = datetime.datetime(
                year=i, month=end.month, day=end.day, hour=end.hour, minute=end.minute, second=end.second)
            subset = df[(df.date_time >= start_date)
                        & (df.date_time <= end_date)]
            Total += subset['kwh'].sum()/(end.year - start.year)

        # sum of kWh in period [21/JUN to 31/DEC] in 2016 and 2017 divide by 2
        for i in range(start.year, end.year):
            start_date = datetime.datetime(
                year=i, month=start.month, day=start.day, hour=start.hour, minute=start.minute, second=start.second)
            end_date = datetime.datetime(
                year=i, month=12, day=31, hour=23, minute=59, second=59)
            subset = df[(df.date_time >= start_date)
                        & (df.date_time <= end_date)]
            Total += subset['kwh'].sum()/(end.year - start.year)

        # sum of kWh in period ]01/FEB to 21/JUN[ in 2017 divided by 1
        for i in range(start.year+1, end.year):
            start_date = datetime.datetime(
                year=i, month=end.month, day=end.day, hour=end.hour, minute=end.minute, second=end.second)
            end_date = datetime.datetime(
                year=i, month=start.month, day=start.day, hour=start.hour, minute=start.minute, second=start.second)
            subset = df[(df.date_time > start_date)
                        & (df.date_time < end_date)]
            Total += subset['kwh'].sum()/(end.year - start.year-1)

    # Example 01/02/2016 - 26/06/2018
    else:

        # sum of kWh in period [01/JAN to 01/FEB] in 2017 and 2018 divide by 2
        for i in range(start.year+1, end.year+1):
            start_date = datetime.datetime(
                year=i, month=1, day=1, hour=0, minute=0, second=0)
            end_date = datetime.datetime(
                year=i, month=start.month, day=start.day, hour=start.hour, minute=start.minute, second=start.second)
            subset = df[(df.date_time >= start_date)
                        & (df.date_time <= end_date)]
            Total += subset['kwh'].sum()/(end.year - start.year)

        # sum of kWh in period [21/JUN to 31/DEC] in 2016, 2017 divide by 2
        for i in range(start.year, end.year):
            start_date = datetime.datetime(
                year=i, month=end.month, day=end.day, hour=end.hour, minute=end.minute, second=end.second)
            end_date = datetime.datetime(
                year=i, month=12, day=31, hour=23, minute=59, second=59)
            subset = df[(df.date_time >= start_date)
                        & (df.date_time <= end_date)]
            Total += subset['kwh'].sum()/(end.year - start.year)

        # sum of kWh in period ]01/FEB to 21/JUN[ in 2016, 2017 and 2018 divide by 3
        for i in range(start.year, end.year+1):
            start_date = datetime.datetime(
                year=i, month=start.month, day=start.day, hour=start.hour, minute=start.minute, second=start.second)
            end_date = datetime.datetime(
                year=i, month=end.month, day=end.day, hour=end.hour, minute=end.minute, second=end.second)
            subset = df[(df.date_time > start_date)
                        & (df.date_time < end_date)]
            Total += subset['kwh'].sum()/(end.year - start.year+1)
    return Total
