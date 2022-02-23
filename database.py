import mysql.connector

#datos de la conexion SQL
def connect_db():
    midb = mysql.connector.connect(
    host="190.228.29.62",
    user="matyacc2",
    password="Agustin_1504",
    database="test-mmspack-almagro"
    )
    return midb