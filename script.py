import mysql.connector
import pandas as pd



def connect_db():
    midb = mysql.connector.connect(
    host="190.228.29.62",
    user="matyacc2 ",
    password="Agustin_1504",
    database="mmspack-almagro"
    )
    cursor = midb.cursor()
    return cursor, midb

def exel_a_lista(nombre_archivo,nombre_hoja):
    data = pd.read_excel(nombre_archivo,sheet_name=nombre_hoja, skiprows=0)
    lista_filtrada = data.fillna("")
    lista_data = lista_filtrada.to_numpy().tolist()
    print(type(lista_data))
    return lista_data

def df_a_lista(data):
    lista_filtrada = data.fillna("")
    lista_data = lista_filtrada.to_numpy().tolist()
    print("lectura finalizada")
    return lista_data

def escribir_ruta(database,nombre_archivo):
    pd.read_sql('SELECT * FROM ViajesGsolutions',database).to_excel(f'{nombre_archivo}.xlsx')





