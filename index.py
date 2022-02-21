from playsound import playsound
from script import *
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import personalizado
import os

ahora = (datetime.today())
fecha_hoy = str(ahora)[0:10]
dia_actual = fecha_hoy[8:10]
mes_actual = fecha_hoy[5:7]
año_actual = fecha_hoy[0:4]
print(dia_actual+"-"+mes_actual+"-"+año_actual)


def insert_pedido(codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,usuario_logistica):
    cursor, midb = connect_db()
    sql = "insert into GSolutions (sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_hoy,usuario_logistica)
    cursor.execute(sql,values)
    midb.commit()
    
    
def subir_archivo(nombre_archivo):
    verificacion = verificar_si_existe()
    lista = exel_a_lista(nombre_archivo,"Hoja1")
    for x in lista:
        cur,db = connect_db()
        if len(verificacion[0]) < 10:
            remito = "SG-0000000000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 100:
            remito = "SG-000000000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 1000:
            remito = "SG-00000000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 10000:
            remito = "SG-0000000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 100000:
            remito = "SG-000000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 1000000:
            remito = "SG-00000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 10000000:
            remito = "SG-0000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 100000000:
            remito = "SG-000" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 1000000000:
            remito = "SG-00" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 10000000000:
            remito = "SG-0" + str(len(verificacion[0]))
        elif len(verificacion[0]) < 100000000000:
            remito = "SG-" + str(len(verificacion[0]))            
        nro_telefono = x[3]
        envios = x[4]
        nombre = x[5]
        apellido = x[6]
        dni = x[7]
        provincia = x[8]
        ciudad = x[9]
        cp = x[10]
        direccion = x[11]
        altura = x[12]
        torre_monoblock = x[13]
        piso = x[14]
        departamento = x[15]
        manzana = x[16]
        casa_lote = x[17]
        barrio = x[18]
        entre_calles = x[19]
        referencia = x[20]
        usuario_logistica = "MMS PACK"
        print(nro_telefono)
        if remito in str(verificacion[0]):
            print("ya existe")
        elif str(nro_telefono) in str(verificacion[1]):
            playsound("sonidos/ok.mp3")
            print(f"\n\n\n{nro_telefono} ya existe\n\nSI - Para cargar un nuevo envio\n\nNO - Para omitir\n\nCancelar - Para terminar el proceso")
            opcion = input()
            if opcion.lower() == "si":
                sim = input("Scanner: ")
                insert_pedido(sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica)
                archivo = "Etiqueta.pdf"
                c = canvas.Canvas(archivo, pagesize=personalizado)
                c.setFont("Helvetica", 16)
                c.drawString(5, 30,direccion + " " + str(altura) + torre_monoblock + " " + piso + " " + departamento)
                if barrio == "":
                    c.drawString(5, 50,ciudad)
                else:
                    c.drawString(5, 50,barrio)
                c.drawString(5, 70,str(nro_telefono))
                c.drawString(5, 90,nombre + " " + apellido)
                c.save()
                os.startfile(archivo,"print")
                verificacion[0].append(remito)
            elif opcion.lower() == "no":
                pass
            elif opcion.lower() == "cancelar":
                exit()
            else: print("opcion incorrecta")
        else:
            verificacion[0].append(remito)
            verificacion[1].append(nro_telefono)
            sim = input("Scanner: ")
            insert_pedido(sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica)
            archivo = "Etiqueta.pdf"
            c = canvas.Canvas(archivo, pagesize=personalizado)
            c.setFont("Helvetica", 16)
            c.drawString(5, 30,direccion + " " + str(altura) + torre_monoblock + " " + piso + " " + departamento)
            if barrio == "":
                c.drawString(5, 50,ciudad)
            else:
                c.drawString(5, 50,barrio)
            c.drawString(5, 70,str(nro_telefono))
            c.drawString(5, 90,nombre + " " + apellido)
            c.save()
            os.startfile(archivo,"print")
    
        

def verificar_si_existe():
    cursor, midb = connect_db()
    lista_remito = []
    lista_telefono = []
    cursor.execute(f"select * from GSolutions")
    resultado = cursor.fetchall()
    for x in resultado:
        lista_remito.append(x[2])
        lista_telefono.append(x[3])
    print(len(lista_remito))
    return [lista_remito, lista_telefono]


def menu():
    menuprint = """
            1-Subir nuevo archivo
            2-Enviar correo con estado de entregas
            """

    print(menuprint)
    opcion = input()
    while opcion.lower() != "fin":
        if opcion == "1":
            archivo = "PLANILLA GLOBAL " + dia_actual+"-"+mes_actual+"-"+año_actual+"-MMS.xlsx"
            subir_archivo(archivo)
            asignaciones = "PLANILLA GLOBAL " + dia_actual+"-"+mes_actual+"-"+año_actual+".xlsx"
            escribir_ruta(asignaciones)
            enviar_correo(["logistica@gsolutions.com.ar"],"Asignación",asignaciones)
            playsound("sonidos/error.mp3")
        elif opcion == "2":
            estados = "PLANILLA GLOBAL " + dia_actual+"-"+mes_actual+"-"+año_actual+".xlsx"
            escribir_ruta(estados)
            enviar_correo(["logistica@gsolutions.com.ar"],"Estado de entregas",estados)
        print(menuprint)
        opcion = input()

menu()