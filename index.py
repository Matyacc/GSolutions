import pandas as pd
from database import connect_db
from playsound import playsound
from script import (escribir_ruta_hoy, subir_archivo, 
                    dia_actual, mes_actual, año_actual, 
                    enviar_correo, borrar_hoy)


def menu():
    menuprint = """
            1-Subir nuevo archivo

            3-Enviar correo de asignaciones (HOY)
            3-Enviar correo con estado de entregas (HOY)
            4-Enviar correo con resumen de un dia determinado

            Comandos especiales:

            "Descargar todo"    /   Descargar archivo con todos los viajes
            "Resetear dia"      /   Para borrar el dia actual escriba  
            "Fin"               /   para salir
            """

    print(menuprint)
    opcion = input()
    while opcion.lower() != "fin":
        if opcion == "1":
            archivo = f"planillas_originales/PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}-MMS.xlsx"
            subir_archivo(archivo)
            playsound("sonidos/error.mp3")
        #envia Correo con asignaciones de chip
        elif opcion == "2":
            asignaciones = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_ruta_hoy(asignaciones)
            enviar_correo(["logistica@gsolutions.com.ar"],"Asignación",asignaciones)
        elif opcion == "3":
            estados = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_ruta_hoy(estados)
            enviar_correo(["logistica@gsolutions.com.ar"],"Estado de entregas",estados)
        
        elif opcion == "4":
            dia = input("ingrese el dia: ")
            mes = input("ingrese el mes: ")
            año = input("ingrese el año: ")
            fecha = f"{año}-{mes}-{dia}"
            _archivo = f"PLANILLA GLOBAL {fecha}.xlsx"
            asunto = f"Resumen del {dia}-{mes}-{año}"
            midb = connect_db()
            pd.read_sql(f'SELECT * FROM GSolutions where fecha_despacho ="{fecha}"',midb).to_excel(f"descargas/{_archivo}")
            enviar_correo(["logistica@gsolutions.com.ar"],asunto,_archivo)
        elif opcion.lower() == "descargar todo":
            archivo = input("Introdusca nombre de archivo: ")
            midb = connect_db()
            pd.read_sql('SELECT * FROM GSolutions',midb).to_excel(f"descargas/{archivo}.xlsx")
        elif opcion.lower() == "resetear dia":
            borrar_hoy()
            print("Todos los registros de hoy fueron eliminados")
        else:
            print("opcion incorrecta")
        print(menuprint)
        opcion = input()

menu()