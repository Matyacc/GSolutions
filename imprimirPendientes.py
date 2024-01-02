from database import connect_db_hostinger
from datetime import datetime,timedelta
from script import enviar_correo
import pandas as pd
from reportlab.pdfgen import canvas
import platform
import os
import qrcode


def enviarCorreoAsignacion(vendedor,fecha):
    if vendedor == "GSolutions":    
        destino = ["logistica@gsolutions.com.ar"]
    if vendedor == "Comunicaciones Cordillera":
        destino = ["s.torres@comcor.com.ar"]
    asignaciones = f"PLANILLA {vendedor}.xlsx"
    escribir_exel(asignaciones,fecha,vendedor)
    enviar_correo(destino,"Asignación",asignaciones)

    
def escribir_exel(nombre_archivo,fechaConsulta,_vendedor):
    midb = connect_db_hostinger()
    # pd.read_sql(f'SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,"BUENOS AIRES",ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where fecha_despacho = {fechaConsulta} and provincia = "{_vendedor}"',midb).to_excel(f'descargas/{nombre_archivo}')
    informe = pd.read_sql(f'select sku,Numero_envío,Telefono,comprador,Direccion,Localidad,CP,Vendedor from ViajesFlexs where Fecha = {fechaConsulta} and Vendedor = "{_vendedor}"',midb)
    informe.to_excel(f'descargas/{nombre_archivo}')

def preparar(vendedor,listaSim):
    midb = connect_db_hostinger()
    cursor = midb.cursor()
    #OBTENGO LA LISTA DE CHIPS QUE SE ENCUENTRAN PENDIENTES DE PREPARAR
    cursor.execute("""select V.Numero_envío,V.Telefono,V.Comprador,V.Localidad,V.Direccion,V.Referencia,
                   "",V.CP,V.id
                from ViajesFlexs AS V inner join historial_estados as H on V.id = H.viajesflexs_id
                where H.id in (select max(H.id) from historial_estados as H 
                                inner join ViajesFlexs as V on V.Numero_envío = H.Numero_envío
                            where V.Vendedor = %s group by H.viajesflexs_id)
                and V.Vendedor = %s and H.estado_envio = 'Lista Para Retirar'""",
                   (vendedor,vendedor))
    for x in cursor.fetchall():
        print(x)
        nroEnvio = x[0]
        telefono = x[1]
        comprador = x[2]
        localidad = x[3]
        direccion = x[4]
        referencia = x[5]
        observacion = x[6]
        cp = x[7]
        viajesflexs_id = x[8]
        #PEDIDO CONFIRMADO SE ENCARGA DE OBTENER EL NUMERO DE SIM A REGISTRAR Y VALIDARLO
        #RECIBE LA LISTA DE TODOS LOS SIMS ASIGNADOS A OTROS ENVIOS
        sim = pedido_confirmado(listaSim)
        listaSim.append(sim)
        archivo_etiqueta = "Etiqueta.pdf"
        generar_etiqueta(direccion,localidad,comprador,telefono,referencia,observacion,cp,nroEnvio,archivo_etiqueta,vendedor)
        try:
            #COMENTO LA LINEA SIGUIENTE PARA HACER TEST Y NO UTILIZAR LA IMPRESORA
            imprimir_etiqueta(archivo_etiqueta)
            try:
                midb = connect_db_hostinger()
                cursor = midb.cursor()
                cursor.execute("update ViajesFlexs set sku = %s where Numero_envío = %s",(sim,nroEnvio))
                midb.commit()
                cursor.execute("""insert into historial_estados (Fecha,Hora,Numero_envío,viajesflexs_id,estado_envio)
                               values (%s,%s,%s,%s)""",
                ((datetime.now()-timedelta(hours=3)).date(),
                               (datetime.now()-timedelta(hours=3)).time(),
                                nroEnvio,viajesflexs_id,"Sectorizado"))
                midb.commit()
                midb.close()
                print("SIM CARGADO")
            except Exception as err:
                print(f"""  
                        Error en actualizar DB ¡¡¡SIM NO CARGADO!!!
                        {telefono}
                        {comprador}
                        {direccion}
                        {localidad}
                        {err}
                    """)
        except:
            print("Error con la impresora")
    enviarCorreoAsignacion(vendedor,"current_date()")



def consultarPendientes():
    midb = connect_db_hostinger()
    cursor = midb.cursor()
    vendedores = []
    simUtilizado = []
    cursor.execute("""select V.Vendedor from ViajesFlexs as V
                   inner join historial_estados as H on V.Numero_envío = H.Numero_envío
                   where H.id in (select max(id) from historial_estados group by Numero_envío)
                    and V.tipo_envio = 15 and H.estado_envio = 'Lista Para Retirar' group by Vendedor""")
    resu = cursor.fetchall()
    cursor.execute("select sku from ViajesFlexs where tipo_envio = 15")
    resuSim = cursor.fetchall()
    midb.close()
    for x in resuSim:
        simUtilizado.append(x[0])
    for x in resu:
        vendor = x[0]
        vendedores.append(vendor) 
    opcion = -1
    return vendedores,simUtilizado
def verificarVendedorElegido(listaVendedores):
    opcion = -1
    while opcion > len(listaVendedores) or opcion <= 0:    
        print("Seleccione el vendedor")
        contador = 1
        for x in listaVendedores:
            print(f"{contador}) {x}")
            contador += 1
        try:
            opcion = int(input())
        except:
            continue
    return listaVendedores[opcion-1]

#verificarEntero devuelve un numero entero ingresado por el usuario
def verificarEntero():
    entero = -1
    try:
        entero = int(input("SCANNER:"))
    except:
        print("EL FORMATO INGRESADO ES INCORRECTO")
        entero = verificarEntero()
    return entero

def pedido_confirmado(_listaSim):
    _sim = verificarEntero()
    while len(str(_sim)) != 19 or _sim == None:
        if _sim != -1:
            print("INGRESO INCORRECTO VUELVA A INTENTAR")
        print("SCANNER:")
        _sim = verificarEntero()
    if _sim in _listaSim:
        print("SIM YA UTILIZADO")
        _sim = pedido_confirmado(_listaSim)
    else:
        return _sim
   
#ajustarTexto() y escribirEtiqueta() son funciones complementarias de generar etiqueta
def ajustarTexto(text,c):
    texto = str(text)
    if len(texto) > 58:
        c.setFont("Helvetica", 6)
    elif len(texto) > 44:
        c.setFont("Helvetica", 8)
    elif len(texto) > 34:
        c.setFont("Helvetica", 10)
    elif len(texto) > 28:
        c.setFont("Helvetica", 12)
    else:
        c.setFont("Helvetica", 16)
def escribirEtiqueta(x,y,text,c):
    texto = str(text)
    if texto != "None":
        c.drawString(x,y,f"{texto}")
        
def generar_etiqueta_OLD(_direccion, _localidad, _comprador,_nro_telefono,_referencia,_observacion,_cp,_nroEnvio,_archivo):
    inch = 72.0
    cm = inch / 2.54
    mm = cm * 0.1
    c = canvas.Canvas(_archivo, pagesize=(100*mm,50*mm))
    ajustarTexto(_nroEnvio,c)
    escribirEtiqueta(5,125,f"{_nroEnvio}",c)
    ajustarTexto(_comprador,c)
    escribirEtiqueta(5, 105,f"{_comprador}",c)
    ajustarTexto(_nro_telefono,c)
    escribirEtiqueta(5, 85,str(_nro_telefono),c)
    ajustarTexto(_referencia,c)
    escribirEtiqueta(5, 65,f"{_referencia}",c)
    ajustarTexto(_observacion,c)
    escribirEtiqueta(5, 45,f"{_observacion}",c)
    ajustarTexto(_direccion,c)
    ajustarTexto(_localidad,c)
    escribirEtiqueta(5,25,str(_direccion),c)
    escribirEtiqueta(5, 5,f"{_cp} {_localidad}",c)
    
    c.save()


def generarQR(_nroEnvio,_vendedor,size,x,y,mm,c,_archivo):
    texto_qr = "{'id':'"+_nroEnvio+"','sender_id':'"+_vendedor+"'}"
    
    # Generar código QR
    qr_data = str(texto_qr)
    qr_code = qrcode.make(qr_data)

    # Guardar código QR como archivo temporal
    temp_filename = "temp_qr_code.png"
    qr_code.save(temp_filename)

    # Tamaño y posición del código QR
    qr_size = size * mm
    qr_x = x * mm
    qr_y = y * mm

    # Dibujar el código QR en la etiqueta
    c.drawImage(temp_filename, qr_x, qr_y, qr_size, qr_size)

    # Eliminar el archivo temporal
    os.remove(temp_filename)


    
    imagen = qrcode.make(texto_qr)
    imagen.save(_archivo)

def imprimir_etiqueta(archivo):
    if format(platform.system()) == "Linux":
                pr=os.popen("lpr", "w") 
                pr.write(archivo)
                pr.close()
    else:
        os.startfile(archivo,"print")


def generar_etiqueta(_direccion, _localidad, _comprador, _nro_telefono, _referencia, _observacion, _cp, _nroEnvio, _archivo,vendedor):
    inch = 72.0
    cm = inch / 2.54
    mm = cm * 0.1
    c = canvas.Canvas(_archivo, pagesize=(100 * mm, 100 * mm))

    # Ajustar tamaño de fuente y escribir campos en la etiqueta
    ajustarTexto(_nroEnvio, c)
    escribirEtiqueta(5, 125, f"{_nroEnvio}", c)
    ajustarTexto(_comprador, c)
    escribirEtiqueta(5, 105, f"{_comprador}", c)
    ajustarTexto(_nro_telefono, c)
    escribirEtiqueta(5, 85, str(_nro_telefono), c)
    ajustarTexto(_referencia, c)
    escribirEtiqueta(5, 65, f"{_referencia}", c)
    ajustarTexto(_observacion, c)
    escribirEtiqueta(5, 45, f"{_observacion}", c)
    ajustarTexto(_direccion, c)
    ajustarTexto(_localidad, c)
    escribirEtiqueta(5, 25, str(_direccion), c)
    escribirEtiqueta(5, 5, f"{_cp} {_localidad}", c)
    
    generarQR(_nroEnvio,vendedor,50,5,50,mm,c,_archivo)

    c.save()

while True:
    listaVendedores,listaSim = consultarPendientes()
    if len(listaVendedores) == 0:
        print("NO HAY CHIP PARA PREPARAR 'r' PARA REIMPRIMIR UNA ETIQUETA o 'reenviar' para volver a enviar el correo de GSolutions")
        option = input()
        if option == "r":
            simReimprimir = verificarEntero()
            while len(str(simReimprimir)) != 19 :
                if simReimprimir != -1:
                    print("INGRESO INCORRECTO VUELVA A INTENTAR")
                print("SCANNER:")
                simReimprimir = verificarEntero()
            midb = connect_db_hostinger()
            cursor = midb.cursor()
            cursor.execute("select Direccion, Localidad, Comprador,Telefono,Referencia,Observacion,CP,Numero_envío,Vendedor from ViajesFlexs where sku = %s",(simReimprimir,))
            resu = cursor.fetchone()
            archivo_etiqueta = "EtiquetaReimpresa.pdf"
            generar_etiqueta(resu[0],resu[1],resu[2],resu[3],resu[4],resu[5],resu[6],resu[7],archivo_etiqueta,resu[8])
            imprimir_etiqueta(archivo_etiqueta)
        elif option == "reenviar":
            print("seleccione el vendedor")
            print("1 GSolutions")
            optionVendedor=input()
            if optionVendedor == "1":
                _vendedor = "GSolutions"
            enviarCorreoAsignacion(_vendedor,"current_date()")
    else: 
        vendedor = verificarVendedorElegido(listaVendedores)
        preparar(vendedor, listaSim)