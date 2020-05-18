from flask import Flask, flash, render_template, request, redirect, url_for, make_response, jsonify, json, g, abort, session, send_from_directory, send_file
from flask_restful import Api
from celery import Celery
import redis
import datetime
import time
from werkzeug.utils import secure_filename
from werkzeug.middleware.shared_data import SharedDataMiddleware
import socket
import os
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine

import protocole_DB
from protocole_DB import ConnexionDB, DeconnexionDB, make_engine, Execute_SQL, Commit
import definition_tables as td
import identification
from celery.signals import worker_process_init
from multiprocessing import current_process
from pathlib import Path
import urllib.parse
import zipfile
import io


url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
r = redis.Redis(host=url.hostname, port=url.port, password=url.password)


UPLOAD_FOLDER = 'tmp'
RESULT_FOLDER = 'tmp/result'
DOWNLOAD_FOLDER = 'tmp/download'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['CELERY_BROKER_URL'] = os.getenv("CELERY_BROKER_URL")
app.config['CELERY_RESULT_BACKEND'] = os.getenv("CELERY_RESULT_BACKEND")

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#-------------------------- Homepage ---------------------------#


@app.route('/', methods=['GET'])
def get_homepage():
    conn, cur = ConnexionDB()
    Execute_SQL(cur, f'SELECT count(id_pa) FROM project_analyse')
    nb_projects = cur.fetchone()[0]
    avg_files = 0
    avg_time_10000 = 0
    categories = list()
    data_norm = list()
    data_stand = list()
    if nb_projects > 0:
        Execute_SQL(cur, f'SELECT count(id_f) FROM files')
        avg_files = round(cur.fetchone()[0]/nb_projects, 1)
        Execute_SQL(cur, "SELECT sum(number_line) AS lines, (sum(normalisation_duration)+sum(standardisation_duration)) AS total_time FROM files WHERE files.status='Analysé'")
        data = cur.fetchone()
        avg_time_10000 = int(round(
            10000*data[1].total_seconds()/float(data[0]), 0))
        Execute_SQL(cur, "SELECT template, sum(number_line) AS lines, sum(normalisation_duration) AS norm, sum(standardisation_duration) AS stand FROM files WHERE files.status='Analysé' GROUP BY template ORDER BY template ASC")
        for row in cur.fetchall():
            categories.append(row[0])
            lines = float(row[1])
            data_norm.append(10000*row[2].total_seconds()/lines)
            data_stand.append(10000*row[3].total_seconds()/lines)
    DeconnexionDB(conn, cur)
    return render_template('homepage.html', nb_projects=nb_projects, avg_files=avg_files, avg_time_10000=avg_time_10000, categories=categories, data_norm=data_norm, data_stand=data_stand)

#-------------------------- Projects Analyses ---------------------------#


@app.route('/projects_analyse', methods=['GET'])
def get_projects_analyse():
    if 'errorMessage' in request.args:
        errorMessage = request.args.get('errorMessage')
    else:
        errorMessage = ""
    engine = make_engine()
    df = pd.read_sql(td.select_project_analyse_all, engine)
    return render_template('pages/projects_analyse.html', tables=[df.to_html(classes='table table-bordered', table_id='dataTableProject', index=False)], errorMessage=errorMessage,)


@app.route("/project_new", methods=["POST"])
def post_project_new():
    conn, cur = ConnexionDB()
    project_name = request.form["project_name"]
    Execute_SQL(cur, td.insert_project_analyse, {'name_pa': project_name})
    Commit(conn)
    DeconnexionDB(conn, cur)
    return redirect(url_for("get_projects_analyse", errorMessage="Nouveau projet créé !!"))


#----------------------- Edit Project -------------------------#

@app.route('/project_edit/<id>', methods=['GET'])
def get_project_edit(id):
    if 'errorMessage' in request.args:
        errorMessage = request.args.get('errorMessage')
    else:
        errorMessage = ""
    conn, cur = ConnexionDB()
    Execute_SQL(cur, f'SELECT name_pa FROM project_analyse WHERE id_pa={id}')
    project_name = cur.fetchone()[0]
    DeconnexionDB(conn, cur)
    engine = make_engine()
    df_files = pd.read_sql(
        f"SELECT id_f as id_file, id_pa as id_projet,status, template, file_type as type, number_line as longueur, normalisation_duration as normalisation, standardisation_duration as standardisation,'' as télécharger, '' supprimer FROM files WHERE id_pa={id};", engine)
    return render_template('pages/project_edit.html', project_name=project_name, tables_files=[df_files.to_html(classes='table table-bordered', table_id='dataTableProjectEditFiles', index=False)], errorMessage=errorMessage, id_pa=id)

#------------------------ Download Files for Project---------------------------#


@app.route('/download_files/<id>', methods=['GET'])
def get_download_files(id):
    engine = make_engine()
    conn, cur = ConnexionDB()
    Execute_SQL(cur, td.select_files_id_with_id_pa, {'id_pa': id})
    all_id_f = cur.fetchall()
    DeconnexionDB(conn, cur)
    Path(os.path.join(
        os.getcwd(), app.config['DOWNLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
    for row in all_id_f:
        id_f = row[0]
        pd.read_sql(f'SELECT date_time, kwh FROM result WHERE id_f={id_f} ORDER BY date_time ASC;', engine).to_csv(
            os.path.join(os.getcwd(), app.config['DOWNLOAD_FOLDER'], f'file_{id_f}.csv'))
    fileobj = io.BytesIO()
    with zipfile.ZipFile(fileobj, 'w') as zip_file:
        for root, dirs, files in os.walk(os.path.join(
                os.getcwd(), app.config['DOWNLOAD_FOLDER'])):
            zip_info = zipfile.ZipInfo(root)
            zip_info.date_time = time.localtime(time.time())[:6]
            zip_info.compress_type = zipfile.ZIP_DEFLATED
            for file in files:
                zip_file.write(os.path.join(root, file), file)
                # with open(os.path.join(root, file), 'rb') as fd:
                #     zip_file.writestr(zip_info, fd.read())
                os.remove(os.path.join(root, file))
    fileobj.seek(0)

    response = make_response(fileobj.read())
    response.headers.set('Content-Type', 'zip')
    response.headers.set('Content-Disposition', 'attachment',
                         filename=f'files_for_project_{id}.zip')
    return response


#------------------------ Remove Project---------------------------#


@app.route('/project_delete/<id>', methods=['GET'])
def get_project_delete(id):
    conn, cur = ConnexionDB()
    Execute_SQL(cur, td.delete_project_analyse, {'id_pa': id})
    Commit(conn)
    DeconnexionDB(conn, cur)
    return redirect(url_for("get_projects_analyse", errorMessage="Le projet et tout les contenus ont bien été supprimé !"))


#------------------------ Remove File---------------------------#

@app.route('/delete_file/<id>', methods=['GET'])
def get_delete_file(id):
    conn, cur = ConnexionDB()
    Execute_SQL(cur, td.select_files_id_pa, {'id_f': id})
    id_pa = cur.fetchone()[0]
    Execute_SQL(cur, td.delete_files, {'id_f': id})
    Execute_SQL(cur, td.delete_result_for_file, {'id_f': id})
    Commit(conn)
    DeconnexionDB(conn, cur)
    return redirect(url_for("get_project_edit", errorMessage="Le fichier et ses résultats ont bien été supprimé !", id=id_pa))

#------------------------ Download File---------------------------#


@app.route('/download_file/<id>', methods=['GET'])
def get_download_file(id):
    engine = make_engine()
    df_file_result = pd.read_sql(
        f'SELECT date_time, kwh FROM result WHERE id_f={id} ORDER BY date_time ASC;', engine)
    resp = make_response(df_file_result.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

#--------------------------- Files -----------------------------#


# @app.route('/files', methods=['GET'])
# def get_files():
#     conn, cur = ConnexionDB()
#     Execute_SQL(cur, "SELECT extract( MONTH FROM date_time) as month, sum(kwh) as conso FROM result WHERE date_time BETWEEN '2019-01-01 00:00:00' AND '2019-12-31 23:30:00' AND id_f IN (SELECT id_f FROM files WHERE file_type = 'consommation' AND id_pa=1) GROUP BY month ORDER BY month;")
#     consommation_data = list()
#     for row in cur.fetchall():
#         consommation_data.append(row[1])
#     Execute_SQL(cur, "SELECT extract( MONTH FROM date_time) as month, sum(kwh) as conso FROM result WHERE date_time BETWEEN '2019-01-01 00:00:00' AND '2019-12-31 23:30:00' AND id_f IN (SELECT id_f FROM files WHERE file_type = 'production' AND id_pa=1) GROUP BY month ORDER BY month;")
#     production_data = list()
#     for row in cur.fetchall():
#         production_data.append(row[1])
#     return render_template('pages/files.html', consommation_data=consommation_data, production_data=production_data)

#---------------------------------------------------------------#


@app.route('/file_add', methods=['POST'])
def get_file_add():
    conn, cur = ConnexionDB()
    file = request.files['file']
    id_pa = request.form["id_pa"]
    if file and allowed_file(file.filename):
        file_type = request.form["file_type"]
        if "supprimer_zero" in request.form:
            supprimer_zero = True
        else:
            supprimer_zero = False
        Execute_SQL(cur, td.insert_files, {
            'id_pa': id_pa, 'file_type': file_type, 'suppression_zero': supprimer_zero})
        Commit(conn)
        id_f = cur.fetchone()[0]
        filename = os.path.join(
            os.getcwd(), app.config['UPLOAD_FOLDER'], str(id_f) + "." + file.filename.rsplit('.', 1)[1].lower())
        Path(os.path.join(
            os.getcwd(), app.config['UPLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
        file.save(filename)
        dispatching_info, df = identification.identification(filename)
        if (not dispatching_info.find("File extension ")):
            errorMessage = "Fichier non valide"
        else:
            file_treatment.apply_async(
                args=[id_f, df.to_json(orient='table'), dispatching_info], countdown=2)

        errorMessage = "Fichier ajouté au projet"
    else:
        errorMessage = "Fichier non valide"
    os.remove(filename)
    return redirect(url_for("get_project_edit", id=id_pa, errorMessage=errorMessage))


#-------------------------- Graph ------------------------------#

@app.route('/graph/<id>', methods=['GET', 'POST'])
def get_graph(id):
    conn, cur = ConnexionDB()
    Execute_SQL(
        cur, f"SELECT extract( MONTH FROM date_time) as month, sum(kwh) as conso FROM result WHERE date_time BETWEEN '2019-01-01 00:00:00' AND '2019-12-31 23:30:00' AND id_f IN (SELECT id_f FROM files WHERE file_type = 'consommation' AND id_pa={id}) GROUP BY month ORDER BY month;")
    consommation_data = [0.0] * 12
    i = 0
    for row in cur.fetchall():
        consommation_data[i] = round(row[1], 3)
        i += 1
    Execute_SQL(
        cur, f"SELECT extract( MONTH FROM date_time) as month, sum(kwh) as conso FROM result WHERE date_time BETWEEN '2019-01-01 00:00:00' AND '2019-12-31 23:30:00' AND id_f IN (SELECT id_f FROM files WHERE file_type = 'production' AND id_pa={id}) GROUP BY month ORDER BY month;")
    production_data = [0.0] * 12
    surplus_data = [0.0] * 12
    i = 0
    for row in cur.fetchall():
        production_data[i] = round(row[1], 3)
        if (consommation_data[i] < production_data[i]):
            surplus_data[i] = production_data[i]-consommation_data[i]
        i += 1
    Execute_SQL(cur, f"SELECT name_pa FROM project_analyse WHERE id_pa={id}")
    name_pa = cur.fetchone()[0]
    return render_template('pages/graph.html', projet=name_pa, consommation_data=consommation_data, production_data=production_data, surplus_data=surplus_data)

#---------------------- Documentation / help --------------------------#


@app.route('/documentation', methods=['GET'])
def get_documentation():
    return render_template('pages/documentation.html')


@app.route('/help', methods=['GET'])
def get_help():
    return render_template('pages/help.html')


#---------------------------------------------------#
#                    Celery Tasks                   #
#---------------------------------------------------#


@celery.task
def file_treatment(id, dfjson, dispatching_info: str):
    start_date = datetime.datetime.now()
    try:
        conn, cur = ConnexionDB()
        engine = make_engine()
        Execute_SQL(cur, td.update_files_in_progress, {'id_f': id})
        df = pd.read_json(dfjson, typ='frame', orient='table')
        # Path(os.path.join(
        #     os.getcwd(), app.config['RESULT_FOLDER'])).mkdir(parents=True, exist_ok=True)
        # df.to_csv(os.path.join(
        #     os.getcwd(), app.config['RESULT_FOLDER'], f'fichier_base_{id}.csv'))
        Commit(conn)
        file_type, identification_duration, preparation_duration, normalisation_duration, standardisation_duration, dataframe, df_result = identification.identification_normalisation_standardisation(
            df, dispatching_info, start_date, "web")
        df_result['id_f'] = id
        df_result.to_sql('result', con=engine, index=False, if_exists='append')
        Commit(conn)
        # dataframe.to_csv(os.path.join(
        #     os.getcwd(), app.config['RESULT_FOLDER'], f'result_normalisation_{id}.csv'))
        # df_result.to_csv(os.path.join(
        #     os.getcwd(), app.config['RESULT_FOLDER'], f'result_{id}.csv'))
        Execute_SQL(cur, td.update_files_done, {'id_f': id, "template": file_type, 'number_line': len(
            dataframe), "normalisation_duration": identification_duration+preparation_duration+normalisation_duration, "standardisation_duration": standardisation_duration})
        Commit(conn)
        DeconnexionDB(conn, cur)
    except Exception as error:
        conn, cur = ConnexionDB()
        Execute_SQL(cur, td.update_files_error, {'id_f': id})
        Commit(conn)
        DeconnexionDB(conn, cur)
        print(error)

#---------------------------------------------------#
#                      The End                      #
#---------------------------------------------------#


if __name__ == '__main__':
    app.run(debug=True)
