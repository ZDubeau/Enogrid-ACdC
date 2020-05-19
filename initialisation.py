""" Projet Enogrid-ACdC """
############################################
""" Module by Zahra
𐤟 Création : 2020-05-05
𐤟 Dernière MàJ : 2020-05-05
"""
############################################


import definition_tables
import protocole_DB
full_actions_list = (definition_tables.drop_project_analyse,
                     definition_tables.drop_files,
                     definition_tables.drop_result,
                     definition_tables.drop_normalisation,
                     definition_tables.project_analyse,
                     definition_tables.files,
                     definition_tables.result,
                     definition_tables.normalisation)

if __name__ == "__main__":
    conn, cur = protocole_DB.ConnexionDB()
    for value in full_actions_list:
        protocole_DB.Execute_SQL(cur, value)
        protocole_DB.Commit(conn)
    protocole_DB.DeconnexionDB(conn, cur)
