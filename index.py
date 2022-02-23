import pandas as pd
from database import connect_db
from playsound import playsound
from script import (subir_archivo, 
                    dia_actual, mes_actual, año_actual, 
                    escribir_ruta, enviar_correo, borrar_hoy)


def menu():
    menuprint = """
            1-Subir nuevo archivo
            2-Enviar correo con estado de entregas
            3-Descargar archivo con todos los viajes


            Comandos especiales:

            "Resetear dia"  Para borrar el dia actual escriba  
            "Fin" para salir
            """

    print(menuprint)
    opcion = input()
    while opcion.lower() != "fin":
        if opcion == "1":
            archivo = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}-MMS.xlsx"
            subir_archivo(archivo)
            playsound("sonidos/error.mp3")
            asignaciones = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_ruta(asignaciones)
            # enviar_correo(["logistica@gsolutions.com.ar"],"Asignación",asignaciones)
        elif opcion == "2":
            estados = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_ruta(estados)
            # enviar_correo(["logistica@gsolutions.com.ar"],"Estado de entregas",estados)
        elif opcion == "3":
            midb = connect_db()
            pd.read_sql('SELECT * FROM GSolutions',midb).to_excel(f"descargas/viajes.xlsx")
        elif opcion.lower() == "resetear dia":
            borrar_hoy()
            print("Todos los registros de hoy fueron eliminados")
        else:
            print("opcion incorrecta")
        print(menuprint)
        opcion = input()

menu()