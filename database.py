import mysql.connector

def connect_db_hostinger():
    midb = mysql.connector.connect(
    host="141.136.39.86",
    user="mmslogis_GS",
    password="12345",
    database="mmslogis_MMSPack"
    )
    return midb

def connect_db():
    midb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Agustin_1504",
    database="MMSPack"
    )
    return midb

# def connect_db():
#     midb = mysql.connector.connect(
#     host="190.228.29.62",
#     user="matyacc",
#     password="Agustin_1504",
#     database="mmspack-almagro"
#     )
#     return midb