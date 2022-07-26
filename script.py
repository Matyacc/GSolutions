from numpy import true_divide
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import personalizado
from database import connect_db, connect_db_hostinger
import os
from reportlab.pdfgen import canvas

def ahora():
    ahora = (datetime.today())
    fecha_hoy = str(ahora)[0:10]
    dia_actual = fecha_hoy[8:10]
    mes_actual = fecha_hoy[5:7]
    año_actual = fecha_hoy[0:4]
    return dia_actual,mes_actual,año_actual,fecha_hoy


def limpiarConsola():
    import os
    import platform
    if format(platform.system()) == "Windows":
        os.system("cls")
    elif format(platform.system()) == "Linux":
        os.system("clear")


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
def escribir_exel(nombre_archivo,fechaConsulta):
    midb = connect_db_hostinger()
    pd.read_sql('SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where fecha_despacho = ' + fechaConsulta,midb).to_excel(f'descargas/{nombre_archivo}')

def enviar_correo(destinos,mensaje_asunto,adjunto):
    remitente = 'mmspackcheck.informes@gmail.com'
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
    archivo_adjunto = open(f"descargas/"+ruta_adjunto, 'rb')
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    adjunto_MIME.set_payload((archivo_adjunto).read())
    encoders.encode_base64(adjunto_MIME)
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)
    mensaje.attach(adjunto_MIME)
    sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    sesion_smtp.starttls()
    sesion_smtp.login('mmspackcheck.informes@gmail.com','vhyrdmvmfpvdgyes')
    texto = mensaje.as_string()
    sesion_smtp.sendmail(remitente, destinatarios, texto)
    sesion_smtp.quit()

#verifica si existe el nro de telefono y el nro de remito en la base de datos
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

def buscador_remito(midb,remito):
    cursor = midb.cursor()
    cursor.execute("select fecha_despacho, remito, direccion, altura, chofer, estado from GSolutions where remito like '%"+remito+"%'")
    resultado = cursor.fetchone()
    fecha = str(resultado[0])
    fecha = f"{fecha[8:10]}{fecha[4:7]}-{fecha[0:4]}"
    remito = resultado[1]
    direccion = f"{resultado[2]} {resultado[3]}"
    chofer = str(resultado[4])
    estado = str(resultado[5])
    resultado = f"{fecha} {remito} {direccion} {chofer} {estado}"
    print(resultado)
 
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

def insert_pedido(codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha,usuario_logistica,midb):
    db = verificar_conexion(midb)
    cursor = db.cursor()
    sql = "insert into GSolutions (sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (codigo_sim,nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha,usuario_logistica,)
    cursor.execute(sql,values)
    db.commit()


def subir_archivo(nombre_archivo,db):
    dia_actual,mes_actual,año_actual,fechaHoy = ahora()
    db = verificar_conexion(db)
    verificacion = verificar_si_existe(db)
    contenidoArchivo = exel_a_lista(nombre_archivo,"Hoja1")
    total_sobres = len(contenidoArchivo)
    print(f"Son {total_sobres} sobres")
    cant_direcciones = 0
    direccion_anterior = ""
    contador = 0
    for pedido in contenidoArchivo:
        remito = generar_nro_remito(verificacion)
        # obtengo los datos de el epedidoel accediendo por posicion
        # arranca en cero la fila A       
        nro_telefono = pedido[3]
        envios = pedido[4]
        if str(envios) != "1" and str(envios) != "0": envios = 1 #<-----Arreglo
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
        if direccion_anterior == f"{direccion} {altura}":
            cant_direcciones = cant_direcciones
        else:
            cant_direcciones += 1
        direccion_anterior = f"{direccion} {altura}"

        if str(nro_telefono) in str(verificacion[1]):
            opcion = consulta_repetido(nro_telefono,fechaHoy,db)
            if opcion.lower() == "si":
                pedido_confirmado(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entre_calles,referencia,fechaHoy,usuario_logistica,db,verificacion)
            else:
                print("pedido omitido")
        else:
            pedido_confirmado(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia,fechaHoy,usuario_logistica,db,verificacion)
        contador += 1
        print(f"{contador} de {total_sobres}")
    print(f"En total son {cant_direcciones} direcciones")
    # asignaciones = f"PLANILLA GLOBAL {dia_actual}-{mes_actual}-{año_actual}.xlsx"
    # escribir_exel(asignaciones,"current_date()")
    # enviar_correo(["logistica@gsolutions.com.ar"],"Asignación",asignaciones)

def consulta_repetido(_nro_telefono,fecha,_db):
    cursor = _db.cursor()
    cursor.execute(f"select fecha_despacho, direccion, altura from GSolutions where nro_telefono = {int(_nro_telefono)}")
    resultado = cursor.fetchall()
    if len(resultado) == 1:
        x = resultado[0]
        if str(x[0]) != str(fecha):
            opcion = "si"
        else:
            opcion = aviso_repetido(_nro_telefono,x)
            
    elif len(resultado) > 1:
        lista_fechas = []
        for x in resultado:
            lista_fechas.append(str(x[0]))
        if str(fecha) not in str(lista_fechas):
            opcion = "si"
        else:
            opcion = aviso_repetido(_nro_telefono,x)
    return opcion

def pedido_confirmado(_remito,_nro_telefono,_envios,_nombre,_apellido,_dni,_provincia,_ciudad,_cp,_direccion,_altura,_torre_monoblock,_piso,_departamento,_manzana,_casa_lote,_barrio,_entre_calles,_referencia,fecha,_usuario_logistica,_db,_verificacion):
    _verificacion[0].append(_remito)
    _verificacion[1].append(_nro_telefono)
    _sim = input("Scanner: ")
    while len(_sim) != 19:
        print(len(_sim))
        _sim = input("Scanner: ")
    insert_pedido(_sim,_remito,_nro_telefono,_envios,_nombre,_apellido,_dni,_provincia,_ciudad,_cp,_direccion,_altura,_torre_monoblock,_piso,_departamento,_manzana,_casa_lote,_barrio,_entre_calles,_referencia,fecha,_usuario_logistica,_db)
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
        remito = "SG-0000000000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 100:
        remito = "SG-000000000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 1000:
        remito = "SG-00000000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 10000:
        remito = "SG-0000000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 100000:
        remito = "SG-000000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 1000000:
        remito = "SG-00000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 10000000:
        remito = "SG-0000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 100000000:
        remito = "SG-000" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 1000000000:
        remito = "SG-00" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 10000000000:
        remito = "SG-0" + str(len(_verificacion[0])+20)
    elif len(_verificacion[0]) < 100000000000:
        remito = "SG-" + str(len(_verificacion[0])+20)
    return remito  

def aviso_repetido(_nro_telefono_,_x_):
    print(f"   {_nro_telefono_} ya existe")
    print(f"{_x_[0]}          {_x_[1]} {_x_[2]}")
    print("""
            SI - Para cargar un nuevo envio
            enter - Para omitir
            
            """)
    opcion = input()
    return(opcion)

def actualizardB(dbConsulta,dbCarga):
    """En el primer parametro se coloca la base de datos que esta actualizada
        y en el segundo parametro se coloca la base de datos a actualizar"""
    try:
        listaDb = []
        listaDbLocal = []
        nroEnvioLocal = []
        nroEnvioDB = []
        cursordbConsulta = dbConsulta.cursor()
        cursordbConsulta.execute("select * from GSolutions")
        for x in cursordbConsulta.fetchall():
            listaDb.append(x)
            nroEnvioDB.append(x[2])
        cursordbCarga = dbCarga.cursor()
        cursordbCarga.execute("select * from GSolutions")
        for y in cursordbCarga.fetchall():
            listaDbLocal.append(y)
            nroEnvioLocal.append(str(y[2]))
        contador = -1
        existe = False
        for z in nroEnvioDB:
            contador = contador +1
            if str(z) in str(nroEnvioLocal):
                existe = True
            if existe == False:
                try:
                    viaje = listaDb[contador]
                    sql = "insert into GSolutions (estado, sim,remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    values = viaje[0], viaje[1], viaje[2], viaje[3], viaje[4], viaje[5], viaje[6], viaje[7], viaje[8], viaje[9], viaje[10], viaje[11], viaje[12], viaje[13], viaje[14], viaje[15], viaje[16], viaje[17], viaje[18], viaje[19], viaje[20], viaje[21], viaje[22]
                    cursordbCarga.execute(sql,values)
                    dbCarga.commit()
                except:
                    print("Error en " + nroEnvioDB[contador])
            existe = False
        return True
    except:
        return False
    