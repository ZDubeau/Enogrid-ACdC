#----------------------------------------------------------#
#                     Projet Enogrid-ACdC                  #
#----------------------------------------------------------#
'''
                  Module by Zahra
                  Creation : 2020-05-05
                  Last update : 2020-05-05
'''
#----------------------------------------------------------#
import definition_tables
import protocole_DB

full_actions_list = (definition_tables.drop_project_analyse,
                     definition_tables.drop_files,
                     definition_tables.drop_files_caracteristics,
                     definition_tables.drop_projects_files_link,
                     definition_tables.drop_result,
                     definition_tables.drop_normalisation,
                     definition_tables.project_analyse,
                     definition_tables.files,
                     definition_tables.files_caracteristics,
                     definition_tables.projects_files_link,
                     definition_tables.result,
                     definition_tables.normalisation)

if __name__ == "__main__":
    conn, cur = protocole_DB.ConnexionDB()
    for value in full_actions_list:
        protocole_DB.Execute_SQL(cur, value)
        protocole_DB.Commit(conn)
    protocole_DB.DeconnexionDB(conn, cur)
