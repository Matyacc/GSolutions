import mysql.connector

def connect_db_hostinger():
    midb = mysql.connector.connect(
    host="109.106.251.113",
    user="mmslogis_GS",
    password="12345",
    database="mmslogis_MMSPack"
    )
    return midb

def connect_db():
    midb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="MMSPack"
    )

    return midb

def verificar_conexion(midb):
    conexion = midb.is_connected()
    while conexion == False:
        try:
            print("Reconectando base de datos")
            midb = connect_db_hostinger()
            conexion = midb.is_connected()
        except Exception as error:
            print(error)
            print("Error en la coneccion")
    return midb

# def connect_db():
#     midb = mysql.connector.connect(
#     host="190.228.29.62",
#     user="matyacc",
#     password="Agustin_1504",
#     database="mmspack-almagro"
#     )
#     return midb
