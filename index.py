from ssl import VerifyFlags
from tabnanny import verbose
from script import *
from datetime import *
from datetime import datetime

ahora = (datetime.today())
fecha_hoy = str(ahora)[0:10]



def insert_pedido(nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,usuario_logistica,cursor,midb):
    sql = "insert into GSolutions (remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_despacho,usuario_logistica) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (nro_envio,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote,barrio,entrecalles,referencia,fecha_hoy,usuario_logistica)
    cursor.execute(sql,values)
    midb.commit()
    
    
def subir_archivo(nombre_archivo,cur,db):
    verificacion = verificar_si_existe(cur)
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
        if remito in str(verificacion[0]):
            print("ya existe")
        elif str(nro_telefono) in str(verificacion[1]):
            print(f"\n\n\n{nro_telefono} ya existe\n\nSI - Para cargar un nuevo envio\n\nNO - Para omitir\n\nCancelar - Para terminar el proceso")
            opcion = input()
            if opcion.lower() == "si":
                insert_pedido(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica,cur,db)
                verificacion[0].append(remito)
            elif opcion.lower() == "no":
                pass
            elif opcion.lower() == "cancelar":
                exit()
            else: print("opcion incorrecta")
        else:
            verificacion[0].append(remito)
            verificacion[1].append(nro_telefono)
            insert_pedido(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica,cur,db)
        

def verificar_si_existe(cursor):
    lista_remito = []
    lista_telefono = []
    cursor.execute(f"select * from GSolutions")
    resultado = cursor.fetchall()
    for x in resultado:
        lista_remito.append(x[2])
        lista_telefono.append(x[3])
    print(len(lista_remito))
    return [lista_remito, lista_telefono]


def menu(cur,db):
    menuprint = """
            1-Subir nuevo archivo
            2-crear archivo de ruta
    """

    print(menuprint)
    opcion = input()
    while opcion.lower() != "fin":
        if opcion == "1":
            archivo = input("Nombre de archivo: ") + ".xlsx"
            subir_archivo(archivo,cur,db)
        elif opcion == "2":
            archivo = input("Nombre de archivo: ")
            escribir_ruta(db,archivo)
        print(menuprint)
        opcion = input()

connect = connect_db()
cursor = connect[0]
midb = connect[1]


def borrar_datos(tabla):
    cursor.execute("truncate table " + tabla)
    midb.commit()
menu(cursor,midb)