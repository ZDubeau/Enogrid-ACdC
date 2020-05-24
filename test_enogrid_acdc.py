import identification as ident
import validation as valid
import pandas as pd
import datetime

option = "standalone"

try:
    def test_template_1_60_min():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/1/Template1-60minutes.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert round(dataframe['kwh'].sum(), 5) == 146.30558
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2016, month=1, day=1, hour=0, minute=55, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2016, month=1, day=5, hour=3, minute=55, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template1-60minutes.csv absent")

try:
    def test_template_30_min():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/1/Template1-30minutes.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert round(dataframe['kwh'].sum(), 5) == 73.15279
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2016, month=1, day=1, hour=0, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2016, month=1, day=3, hour=1, minute=30, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template1-30minutes.csv absent")

try:
    def test_template_1_20_min():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/1/Template1-20min.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert round(dataframe['kwh'].sum(), 5) == 48.76853
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2016, month=1, day=1, hour=0, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2016, month=1, day=2, hour=9, minute=0, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template1-20minutes.csv absent")

try:
    def test_template_1_10_min():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/1/Template1-10min.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert round(dataframe['kwh'].sum(), 5) == 24.38426
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2016, month=1, day=1, hour=0, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2016, month=1, day=1, hour=16, minute=30, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template1-10minutes.csv absent")

try:
    def test_template_1():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template1.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2016, month=1, day=1, hour=0, minute=55, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2016, month=12, day=31, hour=23, minute=55, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template1.csv absent")

try:
    def test_template_2():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template2.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2018, month=1, day=20, hour=0, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2020, month=1, day=19, hour=23, minute=50, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template2.csv absent")

try:
    def test_template_3():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template3.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2018, month=12, day=31, hour=23, minute=53, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2019, month=12, day=31, hour=23, minute=52, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template3.csv absent")

try:
    def test_template_4():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template4.xlsx"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2018, month=12, day=31, hour=23, minute=57, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2019, month=12, day=31, hour=23, minute=53, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template4.xlsx absent")

try:
    def test_template_5():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template5.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2018, month=12, day=31, hour=23, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2020, month=4, day=8, hour=21, minute=50, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template5.csv absent")

try:
    def test_template_6():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template6.xls"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2019, month=1, day=1, hour=0, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2019, month=12, day=31, hour=22, minute=59, second=16)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template6.xls absent")

try:
    def test_template_7():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template7.xlsx"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2016, month=3, day=1, hour=0, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2017, month=2, day=27, hour=23, minute=0, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template7.xlsx absent")

try:
    def test_template_8():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template8.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2019, month=3, day=11, hour=0, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2019, month=4, day=10, hour=23, minute=30, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template8.csv absent")

try:
    def test_template_9():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template9.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2017, month=12, day=31, hour=23, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2019, month=12, day=31, hour=22, minute=30, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template9.csv absent")

try:
    def test_template_4_copy():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template4_copy.xlsx"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert round(dataframe['kwh'].sum(), 5) == 0.04042
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2018, month=12, day=31, hour=23, minute=57, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2019, month=1, day=1, hour=8, minute=17, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template4_copy.xlsx absent")

try:
    def test_template_5_copy():
        filename = "/home/zahra/Simplon/May/Enogrid-ACdC/files_brut/Template5_copy.csv"
        file_type, identification, preparation, normalisation, standardisation, dataframe, df_result = ident.iden_norm_stand(
            filename, option)
        assert round(dataframe['kwh'].sum(), 5) == 1892.33333
        assert dataframe['date_time'][0] == datetime.datetime(
            year=2018, month=12, day=31, hour=23, minute=0, second=0)
        assert dataframe['date_time'][len(dataframe)-1] == datetime.datetime(
            year=2019, month=1, day=1, hour=15, minute=30, second=0)
        assert round(df_result['kwh'].sum(
        ), 2) == round(valid.kwh_on_normalize_df(dataframe), 2)
except:
    print("Fichier Template5_copy.csv absent")
