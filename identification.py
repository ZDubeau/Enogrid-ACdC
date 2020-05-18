import glob
import io
import csv
import sys
import datetime
import pandas as pd
import normalisation as nm
import standardisation as sd


def identification(file):
    extension = str.split(file, '.')[1]
    if extension == 'csv':
        with io.open(file, 'r', encoding='utf-8') as f:
            dispatching_info = str(next(csv.reader(f)))
        df = pd.read_csv(file, sep='delimiter', engine='python')
    elif extension == 'xlsx':
        dispatching_info = str(pd.read_excel(
            file).columns.ravel().tolist())
        df = pd.read_excel(file)
    else:
        dispatching_info = f'File extension {extension} unknown - treatment impossible'
        df = pd.DataFrame(columns=['Date_Time', 'kW'])
    return dispatching_info, df


def iden_norm_stand(file, origin='standalone'):
    start_date = datetime.datetime.now()
    try:
        dispatching_info, df = identification(file)
        if (not dispatching_info.find("File extension ")):
            end_identification_date = datetime.datetime.now()
            traitement = end_identification_date-start_date
            return dispatching_info, traitement, traitement, traitement, traitement, df, pd.DataFrame(columns=['date_time', 'kwh'])
        else:
            return identification_normalisation_standardisation(df, dispatching_info, start_date, origin)
    except Exception as error:
        print(error)
        end_identification_date = datetime.datetime.now()
        traitement = end_identification_date-start_date
        return error, traitement, traitement, traitement, traitement, pd.DataFrame(columns=['Date_Time', 'kW']), pd.DataFrame(columns=['date_time', 'kwh'])


def identification_normalisation_standardisation(df: pd.DataFrame, dispatching_info, start_date, origin="standalone"):
    dispatch = {
        "['\\ufeffdatetime;W']": nm.template1_pd,
        "['Date;Time;W']": nm.template2_pd,
        "['Datetime;W']": nm.template3_pd,
        "['Datetime', 'W']": nm.template4_pd,
        "['\\ufeffHorodate;W']": nm.template5_pd,
        "['Datetime', 'kW']": nm.template6_pd,
        "['Date', 'Time', 'kWh']": nm.template7_pd,
        "['Datetime;W;W']": nm.template8_pd,
        "['Horodate;Wh']": nm.template9_pd}
    try:
        function = dispatch[dispatching_info]
        end_identification_date = datetime.datetime.now()
        dfjson = df.to_json(orient='table')
        df = pd.read_json(dfjson, typ='frame', orient='table')
        file_type, preparation, dataframe = function(df, origin)
        end_import_date = datetime.datetime.now()
        df_result = pd.DataFrame(columns=['date_time', 'kwh'])
        df_result['date_time'] = pd.date_range(
            start='2019-01-01 00:00:00', end='2019-12-31 23:30:00', periods=17520)
        if origin == "standalone":
            df_result = sd.standardisation_one_year_thirty_minutes_multi_processing(
                dataframe, df_result)
        else:
            df_result = sd.standardisation_one_year_thirty_minutes_multi_threading(
                dataframe, df_result)
        end_standard_date = datetime.datetime.now()
        return file_type, end_identification_date-start_date, preparation, end_import_date-end_identification_date, end_standard_date - end_import_date, dataframe, df_result
    except Exception as error:
        end_identification_date = datetime.datetime.now()
        traitement = end_identification_date-start_date
        return error, traitement, traitement, traitement, traitement, pd.DataFrame(columns=['Date_Time', 'kW']), pd.DataFrame(columns=['date_time', 'kwh'])


if __name__ == "__main__":
    file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = iden_norm_stand(
        sys.argv[1], "web")
    dataframe.to_csv('result_normalisation_' +
                     str.split(sys.argv[1], '.')[1]+".csv")
    df_result.to_csv('result_'+str.split(sys.argv[1], '.')[1]+".csv")
    print("Fichier : ", sys.argv[1])
    print("Template : ", file_type)
    print("Identification :", identification)
    print("Preparation :", preparation)
    print("Normalisation :", normalisation)
    print("Standardisation :", standardisation)
