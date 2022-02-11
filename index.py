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
    print(verificacion[1])
    lista = exel_a_lista(nombre_archivo,"Hoja1")
    for x in lista:
        print(verificacion[1])
        remito = "SG-" + str(len(verificacion[0]))
        nro_telefono = x[2]
        envios = x[3]
        nombre = x[4]
        apellido = x[5]
        dni = x[6]
        provincia = x[7]
        ciudad = x[8]
        cp = x[9]
        direccion = x[10]
        altura = x[11]
        torre_monoblock = x[12]
        piso = x[13]
        departamento = x[14]
        manzana = x[15]
        casa_lote = x[16]
        barrio = x[17]
        entre_calles = x[18]
        referencia = x[19]
        usuario_logistica = "MMS PACK"
        print(verificacion)
        print(verificacion[0])
        print(verificacion[1])
        print(remito in verificacion[0])
        print(nro_telefono in verificacion[1])
        if remito in str(verificacion[0]):
            print("ya existe")
        elif str(nro_telefono) in str(verificacion[1]):
            print(f"\n\n\n{nro_telefono} ya existe\n\nSI - Para cargar un nuevo envio\n\nNO - Para omitir\n\nFIN - Para terminar el proceso")
            opcion = input()
            if opcion.lower() == "si":
                insert_pedido(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica,cur,db)
                verificacion[0].append(remito)
            elif opcion.lower() == "no":
                pass
            elif opcion.lower() == "fin":
                exit()
            else: print("opcion incorrecta")
        else:
            verificacion[0].append(remito)
            verificacion[1].append(nro_telefono)
            insert_pedido(remito,nro_telefono,envios,nombre,apellido,dni,provincia,ciudad,cp,direccion,altura,torre_monoblock,piso,departamento,manzana,casa_lote, barrio, entre_calles, referencia, usuario_logistica,cur,db)
        

def verificar_si_existe(cursor):
    lista_remito = []
    lista_telefono = []
    cursor.execute("select * from GSolutions")
    resultado = cursor.fetchall()
    for x in resultado:
        lista_remito.append(x[1])
        lista_telefono.append(x[2])
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
            archivo = input("Nombre de archivo: ") + ".xlsx"
            escribir_ruta(db,archivo)
        print(menuprint)
        opcion = input()

connect = connect_db()
cursor = connect[0]
midb = connect[1]


menu(cursor,midb)