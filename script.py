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
from database import connect_db

ahora = (datetime.today())
fecha_hoy = str(ahora)[0:10]
dia_actual = fecha_hoy[8:10]
mes_actual = fecha_hoy[5:7]
año_actual = fecha_hoy[0:4]
print(dia_actual+"-"+mes_actual+"-"+año_actual)

def formato_fecha(fecha):
    fech = str(fecha)[0:10]
    dia = fech[8:10]
    mes = fech[5:7]
    año = fech[0:4]
    return dia, mes, año
if datetime(1991,9,15) > datetime.today():
    print("todavia falta")
elif datetime(1991,9,15) < datetime.today():

    print("ya paso")
#convierte las filas de un exel en una lista de datos
def exel_a_lista(nombre_archivo,nombre_hoja):
    data = pd.read_excel(nombre_archivo,sheet_name=nombre_hoja, skiprows=0)
    lista_filtrada = data.fillna("")
    lista_data = lista_filtrada.to_numpy().tolist()
    return lista_data

#convierte un DataFrame en una lista
def df_a_lista(data):
    lista_filtrada = data.fillna("")
    lista_data = lista_filtrada.to_numpy().tolist()
    print("lectura finalizada")
    return lista_data

#genera un exel de Gsolutions con los viajes del dia
def escribir_ruta(nombre_archivo):
    midb = connect_db()
    pd.read_sql('SELECT * FROM GSolutions where fecha_despacho = current_date()',midb).to_excel(f'{nombre_archivo}')


#envia un correo con las asignaciones 
# y estado actual del dia en curso
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


#verifica si existe el nro de telefono y 
# el nro de remito en la base de datos
def verificar_si_existe(midb):
    cursor = midb.cursor()
    lista_remito = []
    lista_telefono = []
    cursor.execute("select remito, nro_telefono from GSolutions")
    resultado = cursor.fetchall()
    for x in resultado:
        lista_remito.append(x[0])
        lista_telefono.append(x[1])
    print(len(lista_remito))
    return [lista_remito, lista_telefono]


#la funcion mas importante y compleja
#sube informacion a la base de datos 
def subir_archivo(nombre_archivo):
    db = connect_db()
    verificacion = verificar_si_existe(db)
    lista = exel_a_lista(nombre_archivo,"Hoja1")
    
    for x in lista:
        #genero nro de envio "estetico"
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
        
        # obtengo los datos de el exel accediendo por posicion
        # arranca en cero la fila A       
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
        if ".0" in altura: altura = altura [0:-2] #<-----Arreglo
        torre_monoblock = x[13]
        piso = x[14]
        departamento = x[15]
        manzana = x[16]
        casa_lote = x[17]
        barrio = x[18]
        entre_calles = x[19]
        referencia = x[20]
        usuario_logistica = "MMS PACK"

        #utilizo la lista de verificacion 
        #para controlar si existe el nro de telefono
        if str(nro_telefono) in str(verificacion[1]):
            print(f"   {nro_telefono} ya existe")
            print("")
            cursor = db.cursor()
            cursor.execute(f"select fecha_despacho, direccion, altura from GSolutions where nro_telefono = {int(nro_telefono)}")
            resultado = cursor.fetchall()
            print(len(resultado))
            if len(resultado) == 1:
                x = resultado[0]
                print(f"{x[0]}          {x[1]} {x[2]}")
            elif len(resultado) > 1:
                for x in resultado:
                    print(f"{x[0]}          {x[1]} {x[2]}")
            #opciones a realizar en caso de telefono repetido
            print(       """
            SI - Para cargar un nuevo envio
            Cancelar - Para terminar el proceso""")
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
                # os.startfile(archivo,"print")
                verificacion[0].append(remito)
            elif opcion.lower() == "cancelar":
                exit()
            else:
                pass
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
            # os.startfile(archivo,"print")
    db.close()

def verificar_conexion(midb):
    if midb.is_connected() == False:
        print("Reconectando base de datos")
    while midb.is_connected() == False:
        try:
            midb = connect_db()
            conexion = midb.is_connected()
            print("Conexion exitosa")
        except:
            print("Error en la coneccion")
    return midb


def insert_pedido(codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,usuario_logistica,midb):
    db = verificar_conexion(midb)
    cursor = db.cursor()
    sql = "insert into GSolutions (sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_hoy,usuario_logistica)
    cursor.execute(sql,values)
    db.commit()

def borrar_hoy():
    midb = connect_db()
    cursor = midb.cursor()
    sql = "delete from GSolutions where fecha_despacho = %s"
    values = (f"{año_actual}-{mes_actual}-{dia_actual}",)
    cursor.execute(sql,values)
    midb.commit()