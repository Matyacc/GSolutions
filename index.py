import os
import pandas as pd
from database import connect_db, connect_db_hostinger
from script import buscador_remito, escribir_exel, escribir_exel_desde_local, generar_etiqueta, subir_archivo, ahora, enviar_correo,limpiarConsola,actualizardB,actualizarEstadosDbLocal,selectVendedor
# midb = connect_db()
# cursor = midb.cursor()
# cursor.execute("""CREATE TABLE if not exists`GSolutions` (
#   `estado` varchar(45) DEFAULT NULL,
#   `sim` varchar(30) DEFAULT NULL,
#   `remito` varchar(30) NOT NULL,
#   `nro_telefono` varchar(30) DEFAULT NULL,
#   `envios` int(11) DEFAULT NULL,
#   `nombre` varchar(50) DEFAULT NULL,
#   `apellido` varchar(50) DEFAULT NULL,
#   `dni` int(11) DEFAULT NULL,
#   `provincia` varchar(100) DEFAULT NULL,
#   `ciudad` varchar(100) DEFAULT NULL,
#   `cp` varchar(300) DEFAULT NULL,
#   `direccion` varchar(50) DEFAULT NULL,
#   `altura` varchar(20) DEFAULT NULL,
#   `torre_monoblock` varchar(50) DEFAULT NULL,
#   `piso` varchar(50) DEFAULT NULL,
#   `departamento` varchar(50) DEFAULT NULL,
#   `manzana` varchar(50) DEFAULT NULL,
#   `casa_lote` varchar(50) DEFAULT NULL,
#   `barrio` varchar(50) DEFAULT NULL,
#   `entrecalles` text DEFAULT NULL,
#   `referencia` text DEFAULT NULL,
#   `fecha_despacho` date DEFAULT NULL,
#   `usuario_logistica` varchar(50) DEFAULT NULL,
#   `Chofer` varchar(150) DEFAULT NULL,
#   `correo_chofer` varchar(150) DEFAULT NULL,
#   `precio` double DEFAULT NULL,
#   `costo` double DEFAULT NULL,
#   `Foto` varchar(245) DEFAULT NULL,
#   PRIMARY KEY (`remito`)
# ) ;""")
# midb.commit()
# midb.close()
# actualizardB(False)
# actualizarEstadosDbLocal()
if not (os.path.isdir('descargas')):
    os.system("mkdir descargas")

def menu():
    import platform
    import os
    sistemaOperativo = format(platform.system()) 
    limpiarConsola()
    menuprint = """
            1-Subir nuevo archivo

            2-Enviar correo de asignaciones (HOY)
            3-Enviar correo con estado de entregas (HOY)
            4-Enviar correo con resumen de un dia determinado

            5-Descargar archivo con la informacion de hoy
            6-Descargar archivo con la informacion de un dia determinado
            7-Subir viajes

            Comandos especiales:
            "buscar"            /   Buscar un envio por remito
            "imprimir etiqueta" /   reimprimir una etiqueta
            "Descargar todo"    /   Descargar archivo con todos los viajes
            "Fin"               /   para salir
            """

    print(menuprint)
    opcion = input()
    while opcion.lower() != "fin":
        dia_actual,mes_actual,año_actual,fechaHoy = ahora()
        #subir archivo
        if opcion == "1":
            
            # archivo = f'~/Downloads/PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}-MMS.xlsx'
            archivo = input("arrastre el archivo").replace('"','').replace("'", "")
            vendedor = selectVendedor()
            # if os.path.isfile((os.path.expanduser(archivo))):
            midb = connect_db()
            subir_archivo(archivo,midb,vendedor)
            # else:
            #     print("El archivo no se encuentra en descargas")


        #envia Correo con asignaciones de chip
        elif opcion == "2":
            vendedor = selectVendedor()
            if vendedor == "GSolutions":
                destino = ["logistica@gsolutions.com.ar"]
            if vendedor == "Comunicaciones Cordillera":
                destino = ["s.torres@comcor.com.ar"]
            asignaciones = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_exel_desde_local(asignaciones,"current_date()",vendedor)
            enviar_correo(destino,"Asignación",asignaciones)
            actualizardB(True)

        elif opcion == "3":
            vendedor = selectVendedor()
            if vendedor == "GSolutions":
                destino = ["logistica@gsolutions.com.ar"]
            if vendedor == "Comunicaciones Cordillera":
                destino = ["s.torres@comcor.com.ar"]
            estados = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
            escribir_exel(estados,"current_date()",vendedor)
            enviar_correo(destino,"Estado de entregas",estados)
        
        elif opcion == "4":
            vendedor = selectVendedor()
            if vendedor == "GSolutions":
                destino = ["logistica@gsolutions.com.ar"]
            if vendedor == "Comunicaciones Cordillera":
                destino = ["s.torres@comcor.com.ar"]
            dia = input("ingrese el dia: ")
            mes = input("ingrese el mes: ")
            año = input("ingrese el año: ")
            fecha = f"{dia}-{mes}-{año}"
            fecha_db = f"{año}-{mes}-{dia}"
            archivo = f"PLANILLA GLOBAL {fecha}.xlsx"
            asunto = f"Resumen del {dia}-{mes}-{año}"
            midb = connect_db()
            escribir_exel(archivo,f"'{fecha_db}'")
            midb.close()
            enviar_correo(destino,asunto,archivo)
        
        elif opcion == "5":
            archivo = "PLANILLA GLOBAL(HOY).xlsx"
            midb = connect_db()
            escribir_exel(archivo,"current_date()",vendedor)
            midb.close()
        
        elif opcion == "6":
            vendedor = selectVendedor()
            midb = connect_db()
            dia = input("ingrese el dia: ")
            mes = input("ingrese el mes: ")
            año = input("ingrese el año: ")
            fecha = f"{dia}-{mes}-{año}"
            fecha_db = f"{año}-{mes}-{dia}"
            arcbivo = f"PLANILLA GLOBAL del dia " + fecha + ".xlsx"
            escribir_exel(arcbivo,f"'{fecha_db}'",vendedor)
            midb.close()

        elif opcion == "7":
            actualizardB(True)
        elif opcion.lower() == "buscar":
            limpiarConsola()
            rem = input("Ingrese numero de remito")
            midbbuscador = connect_db()
            buscador_remito(midbbuscador,rem)
        elif opcion.lower() == "descargar todo":
            limpiarConsola()
            archivo = input("Introdusca nombre de archivo: ")
            midb = connect_db()
            pd.read_sql('SELECT * FROM GSolutions',midb).to_excel(f"descargas/{archivo}.xlsx")
            midb.close()
        elif opcion.lower() == "imprimir etiqueta":
            limpiarConsola()
            sim = input("SCANNER: ")
            while sim != "fin":
                midb = connect_db()
                cursor = midb.cursor()
                cursor.execute(f"SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where sim = '" + sim + "';")
                resultado = cursor.fetchone()
                print(resultado)
                archivo_reimprimir_etiqueta = "etiqueta_reimpresa.pdf"
                generar_etiqueta(resultado[11],resultado[12],resultado[18],resultado[9],resultado[5],resultado[6],resultado[3],resultado[13],resultado[14],resultado[15],resultado[16],resultado[17],resultado[18],archivo_reimprimir_etiqueta)
                if sistemaOperativo == "Linux":
                    pr=os.popen("lpr", "w") 
                    pr.write(archivo_reimprimir_etiqueta)
                    pr.close()
                else:
                    os.startfile(archivo_reimprimir_etiqueta,"print")
                sim = input("SCANNER: ")
        else:
            print("opcion incorrecta")
        input("Precione enter para volver al menu principal")
        limpiarConsola()    
        print(menuprint)
        opcion = input()

menu()