#----------------------------------------------------------#
#                     Projet Enogrid-ACdC                  #
#----------------------------------------------------------#
'''
                  Module by Zahra
                  Création : 2020-05-05
                  Dernière MàJ : 2020-05-18
'''
#-------------- Tables des projets analyse ----------------#

drop_project_analyse = """
                      DROP TABLE IF EXISTS project_analyse CASCADE;
                      """

project_analyse = """
                  CREATE TABLE IF NOT EXISTS project_analyse (
                    id_pa SERIAL PRIMARY KEY,
                    name_pa VARCHAR(200)
                  )
                    """

insert_project_analyse = """
                        INSERT INTO project_analyse (name_pa)
                        VALUES (%(name_pa)s) returning id_pa;
                        """

select_project_analyse_all = """
                            SELECT pa.id_pa, name_pa as Nom, prod.nb_prod as Nb_production, conso.nb_conso as Nb_consommation, '' as Editer, MIN(info_status.status) as Statut, '' as Voir, '' as Télécharger, '' as Supprimer
                            FROM project_analyse AS pa 
                            LEFT JOIN (select id_pa,count(file_type) as nb_conso From files WHERE file_type='consommation' GROUP BY id_pa) AS conso 
                            ON pa.id_pa=conso.id_pa 
                            LEFT JOIN (select id_pa,count(file_type) as nb_prod From files WHERE file_type='production' GROUP BY id_pa) AS prod
                            ON pa.id_pa=prod.id_pa
                            LEFT JOIN (select id_pa,(CASE WHEN status='Analysé' Then 100 WHEN status='En cours' THEN 80 WHEN status='Non analysé' THEN 50 ELSE 0 END) AS status From files GROUP BY id_pa,status) AS info_status
                            ON pa.id_pa=info_status.id_pa 
                            GROUP BY pa.id_pa,Nb_production,Nb_consommation ;
                            """

select_project_analyse = """
                        SELECT *
                        FROM project_analyse 
                        WHERE id_pa=%s;
                        """

delete_project_analyse = """
                        DELETE FROM project_analyse 
                        WHERE id_pa=%(id_pa)s; 
                        """

#---------------------- Tables des fichiers ----------------------#

drop_files = """
            DROP TABLE IF EXISTS files CASCADE;
            """

# CASCADE means that the updated values of the referenced column(s) should be copied into the referencing row(s)
files = """
        CREATE TABLE IF NOT EXISTS files (
          id_f SERIAL PRIMARY KEY,
          id_pa INTEGER REFERENCES project_analyse ON DELETE CASCADE,
          file_name VARCHAR(100),
          file_type VARCHAR(20),
          status VARCHAR(20),
          template VARCHAR(200),
          number_line BIGINT,
          normalisation_duration INTERVAL,
          standardisation_duration INTERVAL,
          kwh_one_year_normal FLOAT,
          kwh_one_year_standard FLOAT
        )
      """

insert_files = """
              INSERT INTO files (id_pa, file_name, file_type, status)
              VALUES (%(id_pa)s, %(file_name)s, %(file_type)s, 'Non analysé') returning id_f;
              """

select_files = """
              SELECT * 
              FROM files;
              """

select_files_id_pa = """
                    SELECT id_pa 
                    FROM files 
                    WHERE id_f=%(id_f)s;
                    """

select_files_id_with_id_pa = """
                            SELECT id_f 
                            FROM files 
                            WHERE id_pa=%(id_pa)s;
                            """

update_files_in_progress = """
                          UPDATE files 
                          SET status='En cours' 
                          WHERE id_f=%(id_f)s;
                          """

update_files_error = """
                    UPDATE files 
                    SET status='Erreur' 
                    WHERE id_f=%(id_f)s;
                    """

update_files_done = """
                    UPDATE files 
                    SET status='Analysé', template=%(template)s, number_line=%(number_line)s, normalisation_duration=%(normalisation_duration)s,standardisation_duration=%(standardisation_duration)s,kwh_one_year_normal=%(kwh_one_year_normal)s,kwh_one_year_standard=%(kwh_one_year_standard)s
                    WHERE id_f=%(id_f)s;
                    """

delete_files = """
              DELETE FROM files 
              WHERE id_f=%(id_f)s;
              """

#------------------- Table resultat ---------------------#

drop_result = """
              DROP TABLE IF EXISTS result CASCADE;
              """

# CASCADE means that the updated values of the referenced column(s) should be copied into the referencing row(s)
result = """
          CREATE TABLE IF NOT EXISTS result (
            id SERIAL PRIMARY KEY,
            id_f INTEGER REFERENCES files ON DELETE CASCADE,
            date_time TIMESTAMP,
            kwh FLOAT
          )
        """

insert_result = """
                INSERT INTO result (id_f, date_time, kwh)
                VALUES (%(id_f)s,%(date_time)s,%(kwh)s) returning id;
                """

select_result_for_file = """ 
                        SELECT *
                        FROM result
                        WHERE id_f=%(id_f)s;
                        """

delete_result_for_file = """ 
                        DELETE FROM result 
                        WHERE id_f=%(id_f)s;
                        """

#---------------- Table normalisation ------------------#

drop_normalisation = """
                    DROP TABLE IF EXISTS normalisation CASCADE;
                    """

# CASCADE means that the updated values of the referenced column(s) should be copied into the referencing row(s)
normalisation = """
                CREATE TABLE IF NOT EXISTS normalisation (
                  id SERIAL PRIMARY KEY,
                  id_f INTEGER REFERENCES files ON DELETE CASCADE,
                  date_time TIMESTAMP,
                  kwh FLOAT
                )
                """

insert_normalisation = """
                      INSERT INTO result (id_f, date_time, kwh)
                      VALUES (%(id_f)s,%(date_time)s,%(kwh)s) returning id;
                      """

select_normalisation = """ 
                      SELECT * 
                      FROM normalisation 
                      WHERE id_f=%(id_f)s;
                      """

delete_normalisation = """ 
                      DELETE FROM normalisation 
                      WHERE id_f=%(id_f)s;
                      """
