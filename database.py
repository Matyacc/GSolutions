import mysql.connector

def connect_db():
    midb = mysql.connector.connect(
    host="190.228.29.62",
    user="matyacc2",
    password="Agustin_1504",
    database="mmspack-almagro"
    )
    return midb

