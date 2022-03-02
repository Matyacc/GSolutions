import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from playsound import playsound
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import personalizado
from database import connect_db
import os

ahora = (datetime.today())
fecha_hoy = str(ahora)[0:10]
dia_actual = fecha_hoy[8:10]
mes_actual = fecha_hoy[5:7]
año_actual = fecha_hoy[0:4]
print(dia_actual+"-"+mes_actual+"-"+año_actual)


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
def escribir_ruta_hoy(nombre_archivo):
    midb = connect_db()
    pd.read_sql('SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where fecha_despacho = current_date()',midb).to_excel(f'{nombre_archivo}')

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
   
def generar_etiqueta(_direccion, _altura,_barrio,_ciudad,_nombre,_apellido,_nro_telefono, _torre_monoblock, _piso, _dpto,_manzana, _casa_lote, _entre_calles, _archivo):
    infodir = f"{_direccion} {_altura}"
    infobarrio = f"E/ {_entre_calles}"
    if _torre_monoblock != "" or _casa_lote != "":
        infobarrio = f"E/ {_entre_calles} torre: {_torre_monoblock} casa: {_casa_lote}"
    infodpto = f"Piso: {_piso} dpto: {_dpto}"
    if len(infodpto) < 14:
        infodpto = ""
    localidad = ""
    if _barrio == "":
        localidad = _ciudad
    else:
        localidad = _barrio
    c = canvas.Canvas(_archivo, pagesize=personalizado)
    if (len(_nombre) + len(_apellido)) > 27:
        c.setFont("Helvetica", 12)
    else:
        c.setFont("Helvetica", 16)
    c.drawString(5, 110,f"{_nombre} {_apellido}")
    c.setFont("Helvetica", 16)
    c.drawString(5, 90,str(_nro_telefono))
    if len(infodir) > 44:
        c.setFont("Helvetica", 8)
    elif len(infodir) > 34:
        c.setFont("Helvetica", 10)
    elif len(infodir) > 28:
        c.setFont("Helvetica", 12)
    else:
        c.setFont("Helvetica", 16)
    c.drawString(5, 70,infodir)
    c.setFont("Helvetica", 16)
    c.drawString(5, 50,infodpto)
    if len(infobarrio) > 44:
        c.setFont("Helvetica", 8)
    elif len(infobarrio) > 34:
        c.setFont("Helvetica", 10)
    elif len(infobarrio) > 28:
        c.setFont("Helvetica", 12)
    else:
        c.setFont("Helvetica", 16)
    c.drawString(5, 30,infobarrio)
    c.setFont("Helvetica", 16)
    c.drawString(5, 10,str(localidad))
    c.save()
    
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
    values = (codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_hoy,usuario_logistica,)
    cursor.execute(sql,values)
    db.commit()

def borrar_hoy():
    midb = connect_db()
    cursor = midb.cursor()
    sql = "delete from GSolutions where fecha_despacho = %s"
    values = (f"{año_actual}-{mes_actual}-{dia_actual}",)
    cursor.execute(sql,values)
    midb.commit()

def subir_archivo(nombre_archivo):
    db = connect_db()
    verificacion = verificar_si_existe(db)
    contenidoArchivo = exel_a_lista(nombre_archivo,"Hoja1")
    
    for pedido in contenidoArchivo:
        remito = generar_nro_remito(verificacion)
        # obtengo los datos de el epedidoel accediendo por posicion
        # arranca en cero la fila A       
        nro_telefono = pedido[3]
        envios = pedido[4]
        nombre = pedido[5]
        apellido = pedido[6]
        dni = pedido[7]
        provincia = pedido[8]
        ciudad = pedido[9].lower()
        if "caba" in ciudad or "capital federal" in ciudad or "ciudad de buenos aires" in ciudad or "capital federal (caba)" in ciudad or "ciudad autonoma de buenos aires" in ciudad or "c.a.b.a" in ciudad or "capital" in ciudad: ciudad = "CABA"
        cp = pedido[10]
        direccion = pedido[11]
        altura = str(pedido[12])
        if ".0" in altura: altura = altura [0:-2] #<-----Arreglo
        torre_monoblock = pedido[13]
        piso = pedido[14]
        departamento = pedido[15]
        manzana = pedido[16]
        casa_lote = pedido[17]
        barrio = pedido[18]
        entre_calles = pedido[19]
        referencia = pedido[20]
        usuario_logistica = "MMS PACK"

        if str(nro_telefono) in str(verificacion[1]):
            opcion = consulta_repetido(nro_telefono,db)
            if opcion.lower() == "si":
                pedido_confirmado(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entre_calles,referencia,usuario_logistica,db,verificacion)
            else:
                print("pedido omitido")
                pass
        else:
            pedido_confirmado(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica,db,verificacion)
    db.close()

def consulta_repetido(_nro_telefono,_db):
    cursor = _db.cursor()
    cursor.execute(f"select fecha_despacho, direccion, altura from GSolutions where nro_telefono = {int(_nro_telefono)}")
    resultado = cursor.fetchall()
    if len(resultado) == 1:
        x = resultado[0]
        if str(x[0]) != str(fecha_hoy):
            opcion = "si"
        else:
            opcion = aviso_repetido(_nro_telefono,x)
    elif len(resultado) > 1:
        lista_fechas = []
        for x in resultado:
            lista_fechas.append(str(x[0]))
        if str(fecha_hoy) not in str(lista_fechas):
            opcion = "si"
        else:
            opcion = aviso_repetido(_nro_telefono,x)
    return opcion

def pedido_confirmado(_remito,_nro_telefono,_envios,_nombre,_apellido,_dni,_provincia,_ciudad,_cp,_direccion,_altura,_torre_monoblock,_piso,_departamento,_manzana,_casa_lote,_barrio,_entre_calles,_referencia,_usuario_logistica,_db,_verificacion):
    _verificacion[0].append(_remito)
    _verificacion[1].append(_nro_telefono)
    _sim = input("Scanner: ")
    insert_pedido(_sim,_remito,_nro_telefono,_envios,_nombre,_apellido,_dni,_provincia,_ciudad,_cp,_direccion,_altura,_torre_monoblock,_piso,_departamento,_manzana,_casa_lote,_barrio,_entre_calles,_referencia,_usuario_logistica,_db)
    print(f"Nuevo registro agregado: {_nro_telefono}")
    archivo_etiqueta = "Etiqueta.pdf"
    generar_etiqueta(_direccion,_altura,_barrio,_ciudad,_nombre,_apellido,_nro_telefono,_torre_monoblock,_piso,_departamento,_manzana,_casa_lote,_entre_calles,archivo_etiqueta)
    import platform
    if format(platform.system()) == "Linux":
        pr=os.popen("lpr", "w") 
        pr.write(archivo_etiqueta)
        pr.close()
    else:
        os.startfile(archivo_etiqueta,"print")

def generar_nro_remito(_verificacion):
    if len(_verificacion[0]) < 10:
        remito = "SG-0000000000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 100:
        remito = "SG-000000000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 1000:
        remito = "SG-00000000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 10000:
        remito = "SG-0000000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 100000:
        remito = "SG-000000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 1000000:
        remito = "SG-00000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 10000000:
        remito = "SG-0000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 100000000:
        remito = "SG-000" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 1000000000:
        remito = "SG-00" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 10000000000:
        remito = "SG-0" + str(len(_verificacion[0]))
    elif len(_verificacion[0]) < 100000000000:
        remito = "SG-" + str(len(_verificacion[0]))
    return remito  

def aviso_repetido(_nro_telefono_,_x_):
    #playsound("sonidos/ok.mp3")
    print(f"   {_nro_telefono_} ya existe")
    print(f"{_x_[0]}          {_x_[1]} {_x_[2]}")
    print("""
            SI - Para cargar un nuevo envio
            enter - Para omitir
            
            """)
    opcion = input()
    return(opcion)