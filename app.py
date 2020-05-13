from flask import Flask, flash, render_template, request, redirect, url_for, make_response, jsonify, json, g, abort, session, send_from_directory
from flask_restful import Api
from celery import Celery
import redis
import datetime
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


@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}


UPLOAD_FOLDER = 'uploaded_files'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    return render_template('homepage.html')

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
    Execute_SQL(cur, td.select_files_id_pa, {'id_f': id})
    id_pa = cur.fetchone()
    Execute_SQL(cur, f'SELECT name_pa FROM project_analyse WHERE id_pa={id}')
    project_name = cur.fetchone()[0]
    DeconnexionDB(conn, cur)
    engine = make_engine()
    df_project = pd.read_sql(
        f'SELECT * FROM project_analyse WHERE id_pa={id};', engine)
    df_files = pd.read_sql(
        f"SELECT id_f as id_file, id_pa as id_projet,status, template, file_type as type, number_line as longueur, normalisation_duration as normalisation, standardisation_duration as standardisation,'' as télécharger, '' supprimer FROM files WHERE id_pa={id};", engine)
    return render_template('pages/project_edit.html', project_name=project_name, tables_files=[df_files.to_html(classes='table table-bordered', table_id='dataTableProjectEditFiles', index=False)], errorMessage=errorMessage, id_pa=id)


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


@app.route('/files', methods=['GET'])
def get_files():
    return render_template('pages/files.html')

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
        file_treatment.apply_async(
            args=[id_f, filename], countdown=2)
        errorMessage = "Fichier ajouté au projet"
    else:
        errorMessage = "Fichier non valide"
    return redirect(url_for("get_project_edit", id=id_pa, errorMessage=errorMessage))


#-------------------------- Graph ------------------------------#

@app.route('/graph', methods=['GET', 'POST'])
def get_graph():
    return render_template('pages/graph.html')

#---------------------- Documentation --------------------------#


@app.route('/documentation', methods=['GET'])
def get_documentation():
    return render_template('pages/documentation.html')

#---------------------------------------------------#
#                      Celery Tasks                      #
#---------------------------------------------------#


@celery.task
def file_treatment(id, filename):
    try:
        conn, cur = ConnexionDB()
        engine = make_engine()
        Execute_SQL(cur, td.update_files_in_progress, {'id_f': id})
        Commit(conn)
        file_type, identification_duration, preparation_duration, normalisation_duration, standardisation_duration, dataframe, df_result = identification.identification_normalisation_standardisation(
            filename, "web")
        Execute_SQL(cur, td.update_files_done, {'id_f': id, "template": file_type, 'number_line': len(
            dataframe), "normalisation_duration": identification_duration+preparation_duration+normalisation_duration, "standardisation_duration": standardisation_duration})
        Commit(conn)
        df_result['id_f'] = id
        df_result.to_sql('result', con=engine, index=False, if_exists='append')
        DeconnexionDB(conn, cur)
        os.remove(filename)
    except (KeyError, TypeError, NameError, AttributeError, ZeroDivisionError, IndentationError, IndexError, ValueError) as error:
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
