import glob
import io
import csv
import sys
import datetime
import pandas as pd
import normalisation as nm
import standardisation as sd


def identification_normalisation_standardisation(file,  origin="standalone"):
    start_date = datetime.datetime.now()
    dispatch = {
        "['\\ufeffdatetime;W']": nm.template1,
        "['Date;Time;W']": nm.template2,
        "['Datetime;W']": nm.template3,
        "['Datetime', 'W']": nm.template4,
        "['\\ufeffHorodate;W']": nm.template5,
        "['Datetime', 'kW']": nm.template6,
        "['Date', 'Time', 'kWh']": nm.template7,
        "['Datetime;W;W']": nm.template8,
        "['Horodate;Wh']": nm.template9}
    try:
        if str.split(file, '.')[1] == 'csv':
            with io.open(file, 'r', encoding='utf-8') as f:
                function = dispatch[str(next(csv.reader(f)))]
        elif str.split(file, '.')[1] == 'xlsx':
            function = dispatch[str(pd.read_excel(
                file).columns.ravel().tolist())]
        else:
            quit()
        end_identification_date = datetime.datetime.now()
        file_type, preparation, dataframe = function(file, origin)
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
    except KeyError:
        end_identification_date = datetime.datetime.now()
        traitement = end_identification_date-start_date
        return "Inconnu", traitement, traitement, traitement, traitement, pd.DataFrame(columns=['Date_Time', 'kW']), pd.DataFrame(columns=['date_time', 'kwh'])


if __name__ == "__main__":
    file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = identification_normalisation_standardisation(
        sys.argv[1], "standalone")
    dataframe.to_csv('result_normalisation_'+sys.argv[1])
    df_result.to_csv('result_'+sys.argv[1])
    print("Fichier : ", sys.argv[1])
    print("Template : ", file_type)
    print("Identification :", identification)
    print("Preparation :", preparation)
    print("Normalisation :", normalisation)
    print("Standardisation :", standardisation)
