import mysql.connector
import pandas as pd
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

ahora = (datetime.today())
fecha_hoy = str(ahora)[0:10]



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

def escribir_ruta(nombre_archivo):
    connect = connect_db()
    midb = connect[1]
    pd.read_sql('SELECT * FROM GSolutions where fecha_despacho = "' + fecha_hoy + '"',midb).to_excel(f'{nombre_archivo}')


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