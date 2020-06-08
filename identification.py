import glob
import io
import os
import csv
import sys
import datetime
import pandas as pd
import normalisation as nm
import standardisation as sd
import validation as vd
from pathlib import Path
import re


def identification(file):
    extension = file.suffix
    #extension = str.split(file, '.')[1]
    if extension == '.csv':
        with io.open(file, 'r', encoding='utf-8') as f:
            dispatching_info = str(next(csv.reader(f)))
        df = pd.read_csv(file, sep='delimiter', engine='python')
    elif extension == '.xlsx':
        dispatching_info = str(pd.read_excel(
            file, engine="openpyxl").columns.ravel().tolist())
        df = pd.read_excel(file, engine="openpyxl")
    elif extension == '.xls':
        dispatching_info = str(pd.read_excel(
            file).columns.ravel().tolist())
        df = pd.read_excel(file)
    else:
        dispatching_info = f'File extension {extension} unknown - treatment impossible'
        df = pd.DataFrame(columns=['Date_Time', 'kW'])
    return dispatching_info.replace("\\", ""), df


def iden_norm_stand(file, origin='standalone'):
    start_date = datetime.datetime.now()
    try:
        dispatching_info, df = identification(Path(file))
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
        "['ufeffdatetime;W']": nm.template1,
        "['Date;Time;W']": nm.template2,
        "['Datetime;W']": nm.template3,
        "['Datetime', 'W', 'Unnamed: 2']": nm.template4,
        "['ufeffHorodate;W']": nm.template5,
        "['Datetime', 'kW']": nm.template6,
        "['Date', 'Time', 'kWh']": nm.template7,
        "['Datetime;W;W']": nm.template8,
        "['Horodate;Wh']": nm.template9}
    dataframe = None
    try:
        function = dispatch[dispatching_info]
        end_identification_date = datetime.datetime.now()
        dfjson = df.to_json(orient='table')
        df = pd.read_json(dfjson, typ='frame', orient='table',
                          convert_dates=False, convert_axes=False)
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
        df_result['kwh'] = df_result['kwh'].astype(float)
        end_standard_date = datetime.datetime.now()
        return file_type, end_identification_date-start_date, preparation, end_import_date-end_identification_date, end_standard_date - end_import_date, dataframe, df_result
    except Exception as error:
        end_identification_date = datetime.datetime.now()
        traitement = end_identification_date-start_date
        if dataframe is None:
            return dispatching_info, traitement, traitement, traitement, traitement, pd.DataFrame(columns=['date_time', 'kwh']), pd.DataFrame(columns=['date_time', 'kwh'])
        else:
            return dispatching_info, traitement, traitement, traitement, traitement, dataframe, pd.DataFrame(columns=['date_time', 'kwh'])


if __name__ == "__main__":
    try:
        filepath = Path(sys.argv[1])
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = iden_norm_stand(
            filepath, "standalone")
        Path(os.path.join(
            os.getcwd(), "result")).mkdir(parents=True, exist_ok=True)
        stamp = "_" + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename_result_normalisation = os.path.join(
            os.getcwd(), "result", "result_normalisation_" + filepath.stem + stamp + ".xlsx")
        filename_result = os.path.join(
            os.getcwd(), "result", "result_" + filepath.stem + stamp + ".xlsx")
        dataframe.to_excel(filename_result_normalisation)
        df_result.to_excel(filename_result)
        if len(dataframe) == 0:
            kwh_one_year_normal = 0
        else:
            kwh_one_year_normal = round(
                vd.kwh_on_normalize_df(dataframe), 2)
        kwh_one_year_standard = round(df_result['kwh'].sum(), 2)
        if kwh_one_year_normal == 0:
            ppb = "Normalisation incorrecte"
        else:
            ppb = abs(int(
                round(1000000000*(1-kwh_one_year_standard/kwh_one_year_normal), 0)))
        print("Fichier : ", sys.argv[1])
        print("Template : ", file_type)
        print("Normalisation :", identification+preparation+normalisation)
        print("Standardisation :", standardisation)
        print("Part Per Billion :", ppb)
    except Exception as error:
        print("Traitement impossible :", error)
