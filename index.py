import pandas as pd
from database import connect_db
from playsound import playsound
from script import (escribir_ruta_hoy, generar_etiqueta, subir_archivo, 
                    dia_actual, mes_actual, año_actual, 
                    enviar_correo, borrar_hoy)

def menu():
    menuprint = """
            1-Subir nuevo archivo

            2-Enviar correo de asignaciones (HOY)
            3-Enviar correo con estado de entregas (HOY)
            4-Enviar correo con resumen de un dia determinado

            Comandos especiales:

            "imprimir etiqueta" /   reimprimir una etiqueta
            "Descargar todo"    /   Descargar archivo con todos los viajes
            "Resetear dia"      /   Para borrar el dia actual escriba  
            "Fin"               /   para salir
            """

    print(menuprint)
    opcion = input()
    while opcion.lower() != "fin":
        if opcion == "1":
            try:
                archivo = f"C:/Users/Mi pc/Downloads/PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}-MMS.xlsx"
                subir_archivo(archivo)
            except:
                print("No se encuentra el archivo en Descargas")
            try:
                playsound("sonidos/fin.mp3")
            except:
                print("¡se produjo un error al intentar reproducir el sonido!")
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
            fecha = f"{dia}-{mes}-{año}"
            fecha_db = f"{año}-{mes}-{dia}"
            archivo = f"PLANILLA GLOBAL {fecha}.xlsx"
            asunto = f"Resumen del {dia}-{mes}-{año}"
            midb = connect_db()
            pd.read_sql(f'SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where fecha_despacho ="{fecha_db}"',midb).to_excel(f"descargas/{archivo}")
            midb.close()
            enviar_correo(["logistica@gsolutions.com.ar"],asunto,archivo)
        elif opcion == "5":
            archivo = f"descargas/PLANILLA GLOBAL.xlsx"
            midb = connect_db()
            pd.read_sql(f'SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where fecha_despacho =current_date()',midb).to_excel(archivo)
            midb.close()
        elif opcion.lower() == "descargar todo":
            archivo = input("Introdusca nombre de archivo: ")
            midb = connect_db()
            pd.read_sql('SELECT * FROM GSolutions',midb).to_excel(f"descargas/{archivo}.xlsx")
            midb.close()
        elif opcion.lower() == "resetear dia":
            borrar_hoy()
            print("Todos los registros de hoy fueron eliminados")
        elif opcion.lower() == "imprimir etiqueta":
            sim = input("SCANNER: ")
            while sim != "fin":
                midb = connect_db()
                cursor = midb.cursor()
                cursor.execute(f"SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where sim = '" + sim + "';")
                resultado = cursor.fetchone()
                print(resultado)
                archivo_reimprimir_etiqueta = "etiqueta_reimpresa.pdf"
                generar_etiqueta(resultado[11],resultado[12],resultado[18],resultado[9],resultado[5],resultado[6],resultado[3],resultado[13],resultado[14],resultado[15],resultado[16],resultado[17],resultado[18],archivo_reimprimir_etiqueta)
                import platform
                import os
                if format(platform.system()) == "Linux":
                    pr=os.popen("lpr", "w") 
                    pr.write(archivo_reimprimir_etiqueta)
                    pr.close()
                else:
                    os.startfile(archivo_reimprimir_etiqueta,"print")
                sim = input("SCANNER: ")
        else:
            print("opcion incorrecta")
        print(menuprint)
        opcion = input()

menu()