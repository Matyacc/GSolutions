import mysql.connector
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from playsound import playsound
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import personalizado


ahora = (datetime.today())
fecha_hoy = str(ahora)[0:10]
dia_actual = fecha_hoy[8:10]
mes_actual = fecha_hoy[5:7]
año_actual = fecha_hoy[0:4]
print(dia_actual+"-"+mes_actual+"-"+año_actual)




def connect_db():
    midb = mysql.connector.connect(
    host="190.228.29.62",
    user="matyacc",
    password="Agustin_1504",
    database="mmspack-almagro"
    )
    return midb

def exel_a_lista(nombre_archivo,nombre_hoja):
    data = pd.read_excel(nombre_archivo,sheet_name=nombre_hoja, skiprows=0)
    lista_filtrada = data.fillna("")
    lista_data = lista_filtrada.to_numpy().tolist()
    return lista_data

def df_a_lista(data):
    lista_filtrada = data.fillna("")
    lista_data = lista_filtrada.to_numpy().tolist()
    print("lectura finalizada")
    return lista_data

def escribir_ruta(nombre_archivo):
    midb = connect_db()
    pd.read_sql('SELECT * FROM GSolutions where fecha_despacho = "' + fecha_hoy + '"',midb).to_excel(f'{nombre_archivo}')


def verificar_si_existe(midb):
    cursor = midb.cursor()
    lista_remito = []
    lista_telefono = []
    cursor.execute("select * from GSolutions")
    resultado = cursor.fetchall()
    for x in resultado:
        lista_remito.append(x[2])
        lista_telefono.append(x[3])
    print(len(lista_remito))
    return [lista_remito, lista_telefono]

def enviar_correo(destinos,mensaje_asunto,adjunto):
    """Se deben agregar 3 parametros: destinos, asunto y archivo adjunto
        si los destinos son mas de uno tiene que ponerse en forma de lista"""
    remitente = 'mmspackcheck@gmail.com'
    destinatarios = destinos
    asunto = mensaje_asunto
    cuerpo = ""
    ruta_adjunto = adjunto
    nombre_adjunto = adjunto
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    archivo_adjunto = open(ruta_adjunto, 'rb')
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    adjunto_MIME.set_payload((archivo_adjunto).read())
    encoders.encode_base64(adjunto_MIME)
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)
    mensaje.attach(adjunto_MIME)
    sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    sesion_smtp.starttls()
    sesion_smtp.login('mmspackcheck@gmail.com','abcd1234IMPO')
    texto = mensaje.as_string()
    sesion_smtp.sendmail(remitente, destinatarios, texto)
    sesion_smtp.quit()


def subir_archivo(nombre_archivo):
    db = connect_db()
    verificacion = verificar_si_existe(db)
    lista = exel_a_lista(nombre_archivo,"Hoja1")
    for x in lista:
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
        altura = str(x[12])
        if ".0" in altura:
            altura = altura [0:-2]
        torre_monoblock = x[13]
        piso = x[14]
        departamento = x[15]
        manzana = x[16]
        casa_lote = x[17]
        barrio = x[18]
        entre_calles = x[19]
        referencia = x[20]
        usuario_logistica = "MMS PACK"
        if str(nro_telefono) in str(verificacion[1]):
            print(f"\n\n\n{nro_telefono} ya existe\n\nSI - Para cargar un nuevo envio\n\nNO - Para omitir\n\nCancelar - Para terminar el proceso")
            playsound("sonidos/ok.mp3")
            opcion = input()
            if opcion.lower() == "si":
                sim = input("Scanner: ")
                insert_pedido(sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica,db)
                archivo = "Etiqueta.pdf"
                c = canvas.Canvas(archivo, pagesize=personalizado)
                c.setFont("Helvetica", 14)
                c.drawString(5, 30,f"{direccion} {altura} {torre_monoblock} {piso} {departamento}")
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
            insert_pedido(sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica,db)
            print(f"Nuevo registro agregado: {nro_telefono}")
            archivo = "Etiqueta.pdf"
            c = canvas.Canvas(archivo, pagesize=personalizado)
            c.setFont("Helvetica", 14)
            c.drawString(5, 30,f"{direccion} {altura} {torre_monoblock} {piso} {departamento}")
            if barrio == "":
                c.drawString(5, 50,str(ciudad))
            else:
                c.drawString(5, 50,str(barrio))
            c.drawString(5, 70,str(nro_telefono))
            c.drawString(5, 90,f"{nombre} {apellido}")
            c.save()
            os.startfile(archivo,"print")
    db.close()

def insert_pedido(codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,usuario_logistica,midb):
    if midb.is_connected() == False:
        print("Reconectando base de datos")
    while midb.is_connected() == False:
        try:
            midb = connect_db()
            conexion = midb.is_connected()
        except:
            conexion = midb.is_connected()
        finally:
            print(conexion)
    cursor = midb.cursor()
    sql = "insert into GSolutions (sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_hoy,usuario_logistica)
    cursor.execute(sql,values)
    midb.commit()