#----------------------------------------------------------#
#                     Projet Enogrid-ACdC                  #
#----------------------------------------------------------#
'''
                  Module by Zahra
                  Creation : 2020-05-05
                  Last update : 2020-05-18
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
                            SELECT pa.id_pa, name_pa as Nom, 
                                   SUM(CASE WHEN f.file_type='production' THEN 1 ELSE 0 END) as Nb_production, 
                                   SUM(CASE WHEN f.file_type='consommation' THEN 1 ELSE 0 END) as Nb_consommation,
                                  '' as Editer, 
                                   MIN(CASE WHEN fc.status='Analysé' Then 100 WHEN fc.status='En cours' THEN 80 WHEN fc.status='Non analysé' THEN 50 ELSE 0 END) as Statut, 
                                   '' as Voir, '' as Télécharger, '' as Supprimer
                            FROM project_analyse AS pa
                            LEFT JOIN projects_files_links AS pfl ON pa.id_pa=pfl.id_pa
                            LEFT JOIN files AS f ON pfl.id_f = f.id_f
                            LEFT JOIN files_caracteristics AS fc ON pfl.id_f=fc.id_f
                            GROUP BY pa.id_pa;
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

drop_files_caracteristics = """
                            DROP TABLE IF EXISTS files_caracteristics CASCADE;
                            """

# CASCADE means that the updated values of the referenced column(s) should be copied into the referencing row(s)
files = """
        CREATE TABLE IF NOT EXISTS files (
          id_f SERIAL PRIMARY KEY,
          file_name VARCHAR(100),
          file_type VARCHAR(20)
        )
      """

files_caracteristics = """
                        CREATE TABLE IF NOT EXISTS files_caracteristics (
                          id_f_c SERIAL PRIMARY KEY,
                          id_f INTEGER REFERENCES files ON DELETE CASCADE,
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
              INSERT INTO files (file_name, file_type)
              VALUES ( %(file_name)s, %(file_type)s) returning id_f;
              """

insert_files_caracteristics = """
                              INSERT INTO files_caracteristics (id_f, status)
                              VALUES (%(id_f)s, 'Non analysé') returning id_f_c;
                              """

select_files = """
              SELECT * 
              FROM files;
              """

update_files_in_progress = """
                          UPDATE files_caracteristics 
                          SET status='En cours' 
                          WHERE id_f=%(id_f)s;
                          """

update_files_error = """
                      UPDATE files_caracteristics 
                      SET status='Erreur' 
                      WHERE id_f=%(id_f)s;
                      """

update_files_done = """
                    UPDATE files_caracteristics 
                    SET status='Analysé', template=%(template)s, number_line=%(number_line)s, normalisation_duration=%(normalisation_duration)s,standardisation_duration=%(standardisation_duration)s,kwh_one_year_normal=%(kwh_one_year_normal)s,kwh_one_year_standard=%(kwh_one_year_standard)s
                    WHERE id_f=%(id_f)s;
                    """

delete_files = """
                DELETE FROM files 
                WHERE id_f=%(id_f)s;
                """

#---------------------- Tables des liens projets fichiers ----------------------#
drop_projects_files_link = """
                          DROP TABLE IF EXISTS projects_files_links CASCADE;
                          """

# CASCADE means that the updated values of the referenced column(s) should be copied into the referencing row(s)
projects_files_link = """
                      CREATE TABLE IF NOT EXISTS projects_files_links (
                        id_p_f_l SERIAL PRIMARY KEY,
                        id_pa INTEGER REFERENCES project_analyse ON DELETE CASCADE,
                        id_f INTEGER REFERENCES files ON DELETE CASCADE
                      )
                    """

insert_projects_files_links = """
                              INSERT INTO projects_files_links (id_pa, id_f)
                              VALUES (%(id_pa)s, %(id_f)s) returning id_p_f_l;
                              """

select_files_id_pa = """
                    SELECT id_pa 
                    FROM projects_files_links 
                    WHERE id_f=%(id_f)s;
                    """

select_files_id_with_id_pa = """
                            SELECT id_f 
                            FROM files 
                            WHERE id_pa=%(id_pa)s;
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
