import mysql.connector

def connect_db():
    midb = mysql.connector.connect(
    host="141.136.39.86",
    user="mmslogis_GS",
    password="12345",
    database="mmslogis_MMSPack"
    )
    return midb

