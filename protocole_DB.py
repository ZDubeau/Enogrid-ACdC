""" Projet Enogrid-ACdC """
#---------------------------------------------#
""" Module by Zahra
𐤟 Création : 2020-05-05
𐤟 Dernière MàJ : 2020-05-10
"""
#--------------------------------------------#




from sqlalchemy.engine import url as sqla_url
from sqlalchemy import create_engine
import os
from psycopg2 import Error
import psycopg2
import psycopg2.extras, sys, json
def ConnexionDB():
    dbname = os.getenv("DB_NAME")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORTE")
    try:
        conn = psycopg2.connect(dbname=dbname, user=user,
                                password=password, host=host, port=port)
    except psycopg2.Error as error:
        print("connection impossible !!!", error)
        sys.exit()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #print("Connection :",conn,"Curseur :", cur)
    return conn, cur


def DeconnexionDB(conn, cur):
    cur.close()
    conn.close()

################ Générale ################


def Commit(conn):
    conn.commit()


def Execute_SQL(cur, CodeSQL, MonTuple=()):
    cur.execute(CodeSQL, MonTuple)


def Query_SQL(cur, CodeSQL, MonTuple):
    cur.execute(CodeSQL, MonTuple)
    return cur.fetchall()


def Insert_SQL(cur, CodeSQL, dico):
    try:
        cur.execute(CodeSQL, dico)
        Commit()
        return "OK"
    except (psycopg2.Error, AttributeError) as Error:
        return Error


def Update_SQL(cur, CodeSQL, dico):
    try:
        cur.execute(CodeSQL, dico)
        Commit()
        return "OK"
    except (psycopg2.Error, AttributeError) as Error:
        return Error

################ Tables ################


def Create_Table(cur, CodeSQL):
    try:
        cur.execute(CodeSQL)
        Commit()
        return "OK"
    except (psycopg2.Error, AttributeError) as Error:
        return Error


def Drop_Table(cur, table):
    try:
        sql = f"""DROP TABLE IF EXISTS {table}"""
        cur.execute(sql)
    except (psycopg2.Error, AttributeError) as Error:
        print(Error)


def Drop_Table_Casscade(cur, table):
    try:
        sql = f"""DROP TABLE IF EXISTS {table} CASCADE"""
        cur.execute(sql)
    except (psycopg2.Error, AttributeError) as Error:
        print(Error)


def Delete(cur, table, condition, MonTuple):
    cur.execute(f"""DELETE FROM {table} WHERE {condition} = %s;""", MonTuple)
    Commit()

########### SQLAlchemy engine for pandas #############


def make_engine():
    db_connect_url = sqla_url.URL(
        drivername='postgresql+psycopg2',
        username=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORTE"),
        database=os.getenv("DB_NAME"))
    try:
        # Create engine for postgreSQL
        engine = create_engine(db_connect_url, echo=False)
    except:
        print("Connection impossible !")
        sys.exit()
    return engine

################ Fin ################
