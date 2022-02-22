from script import *


def menu():
    menuprint = """
            1-Subir nuevo archivo
            2-Enviar correo con estado de entregas
            """

    print(menuprint)
    opcion = input()
    while opcion.lower() != "fin":
        if opcion == "1":
            archivo = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}-MMS.xlsx"
            subir_archivo(archivo)
            asignaciones = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_ruta(asignaciones)
            enviar_correo(["logistica@gsolutions.com.ar"],"Asignación",asignaciones)
            playsound("sonidos/error.mp3")
        elif opcion == "2":
            estados = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_ruta(estados)
            enviar_correo(["logistica@gsolutions.com.ar"],"Estado de entregas",estados)
        print(menuprint)
        opcion = input()

menu()