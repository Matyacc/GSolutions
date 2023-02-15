from database import connect_db, connect_db_hostinger,verificar_conexion
from script import enviar_correo
from reportlab.pdfgen import canvas
import pandas as pd
from datetime import datetime
import platform
import os

def escribir_exel(nombre_archivo,fechaConsulta,_vendedor):
    midb = connect_db_hostinger()
    # pd.read_sql(f'SELECT estado, sim, remito, nro_telefono,envios,nombre,apellido,dni,"BUENOS AIRES",ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica FROM GSolutions where fecha_despacho = {fechaConsulta} and provincia = "{_vendedor}"',midb).to_excel(f'descargas/{nombre_archivo}')
    informe = pd.read_sql(f'select sku,Numero_envío,Telefono,comprador,Direccion,Localidad,CP,Vendedor from ViajesFlexs where Fecha = {fechaConsulta} and Vendedor = "{_vendedor}"',midb)
    informe.to_excel(f'descargas/{nombre_archivo}')





def consultarPendientes():
    midb = connect_db_hostinger()
    cursor = midb.cursor()
    vendedores = []
    simUtilizado = []
    cursor.execute("select Vendedor from ViajesFlexs where tipo_envio = 15 and estado_envio = 'Lista Para Retirar' group by Vendedor")
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
def preparar(vendedor,listaSim):
    midb = connect_db_hostinger()
    cursor = midb.cursor()
    #OBTENGO LA LISTA DE CHIPS QUE SE ENCUENTRAN PENDIENTES DE PREPARAR
    cursor.execute("select Numero_envío,Telefono,Comprador,Localidad,Direccion,Referencia,Observacion,CP from ViajesFlexs where Vendedor = %s and estado_envio = 'Lista Para Retirar'",(vendedor,))
    for x in cursor.fetchall():
        nroEnvio = x[0]
        telefono = x[1]
        comprador = x[2]
        localidad = x[3]
        direccion = x[4]
        referencia = x[5]
        observacion = x[6]
        cp = x[7]
        #PEDIDO CONFIRMADO SE ENCARGA DE OBTENER EL NUMERO DE SIM A REGISTRAR Y VALIDARLO
        #RECIBE LA LISTA DE TODOS LOS SIMS ASIGNADOS A OTROS ENVIOS
        sim = pedido_confirmado(listaSim)
        listaSim.append(sim)
        archivo_etiqueta = "Etiqueta.pdf"
        generar_etiqueta(direccion,localidad,comprador,telefono,referencia,observacion,cp,vendedor,archivo_etiqueta)
        generarQR(nroEnvio,vendedor,"imagenQR.pdf")
        try:
            #COMENTO LA LINEA SIGUIENTE PARA HACER TEST Y NO UTILIZAR LA IMPRESORA
            imprimir_etiqueta(archivo_etiqueta)
            # imprimir_etiqueta("imagenQR.pdf")
            try:
                midb = connect_db_hostinger()
                cursor = midb.cursor()
                cursor.execute("update ViajesFlexs set sku = %s,estado_envio = 'Listo para salir (Sectorizado)' where Numero_envío = %s",(sim,nroEnvio))
                midb.commit()
                midb.close()
            except:
                print(f"""  
                        Error en actualizar DB ¡¡¡SIM NO CARGADO!!!
                        {telefono}
                        {comprador}
                        {direccion}
                        {localidad}
                    """)
        except:
            print("Error con la impresora")
    if vendedor == "GSolutions":    
        destino = ["logistica@gsolutions.com.ar"]
    if vendedor == "Comunicaciones Cordillera":
        destino = ["s.torres@comcor.com.ar"]
    asignaciones = f"PLANILLA {vendedor}.xlsx"
    escribir_exel(asignaciones,"current_date()",vendedor)
    enviar_correo(destino,"Asignación",asignaciones)
#verificarEntero devuelve un numero entero ingresado por el usuario
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
    while len(str(_sim)) != 19 :
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
def generar_etiqueta(_direccion, _localidad, _comprador,_nro_telefono,_referencia,_observacion,_cp,_vendedor,_archivo):
    inch = 72.0
    cm = inch / 2.54
    mm = cm * 0.1
    c = canvas.Canvas(_archivo, pagesize=(100*mm,50*mm))
    ajustarTexto(_vendedor,c)
    escribirEtiqueta(5,125,f"{_vendedor}",c)
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
import qrcode
def generarQR(_nroEnvio,_vendedor,_archivo):
    texto_qr = f"'id':'{_nroEnvio}','sender_id':'{_vendedor}'"
    imagen = qrcode.make(texto_qr)
    imagen.save(_archivo)
def imprimir_etiqueta(archivo):
    if format(platform.system()) == "Linux":
                pr=os.popen("lpr", "w") 
                pr.write(archivo)
                pr.close()
    else:
        os.startfile(archivo,"print")



while True:
    listaVendedores,listaSim = consultarPendientes()
    if len(listaVendedores) == 0:
        print("NO HAY CHIP PARA PREPARAR")
        input()
    else:
        vendedor = verificarVendedorElegido(listaVendedores)
        preparar(vendedor,listaSim)