# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def getListaCliMes(db_conn, mes, anio, iumbral, iintervalo, use_prepare, break0, niter):

    # TODO: implementar la consulta; asignar nombre 'cc' al contador resultante
    consulta = " ... "
    
    # TODO: ejecutar la consulta 
    # - mediante PREPARE, EXECUTE, DEALLOCATE si use_prepare es True
    # - mediante db_conn.execute() si es False

    # Array con resultados de la consulta para cada umbral
    dbr=[]

    for ii in range(niter):

        # TODO: ...

        # Guardar resultado de la query
        dbr.append({"umbral":iumbral,"contador":res['cc']})

        # TODO: si break0 es True, salir si contador resultante es cero
        
        # Actualizacion de umbral
        iumbral = iumbral + iintervalo
                
    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)

    resultproxy.close()  

    db_conn.close()  

    return a
    
def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()
    
    db_conn.close()  

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}
    
def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):

    # Array de trazas a mostrar en la página
    dbr=[]

    # Conexión a la base de datos con autocommit en false
    db_conn = db_engine.connect()

    # Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()

    try:
        # Ejecutar consultas
        # Comprobamos si hay que hacer el comienzo de la transacción con SQL o con SQLAlchemy
        if (bSQL):
            db_conn.execute("Begin")
            dbr.append("Comenzamos la transacción con SQL")

        else:
            transaccion = db_conn.begin()
            dbr.append("Comenzamos la transacción con SQLAlchemy")

        # Conseguimos los pedidos realizados por el usuario que queremos borrar
        db_orders = list(db_conn.execute("Select orderid from orders where customerid = '" + str(customerid) + "'"))

        # Borramos los detalles de los pedidos del usuario (en la tabla orderdetail)
        for orderid in db_orders:
            db_conn.execute("Delete from orderdetail where orderid = '" + str(orderid[0]) + "'")

        dbr.append("Borramos los detalles de los pedidos del usuario")

        # Comprobamos si queremos que la transacción falle o no
        if (bFallo):
            # Falla la transacción, comprobamos si hay que hacer commit intermedio
            if (bCommit):
                if (bSQL):
                    # Con SQL hacemos commit seguido de begin
                    db_conn.execute("Commit")
                    db_conn.execute("Begin")
                    dbr.append("Hacemos un commit intermedio con SQL")

                else:
                    # Con SQLAlchemy hacemos commit seguido de begin
                    transaccion.commit()
                    transaccion = db_conn.begin()
                    dbr.append("Hacemos un commit intermedio con SQLAlchemy")

            # Hacemos que la transicción falle borrando el customerid antes que la order
            db_conn.execute("Delete from customers where customerid = '" + str(customerid) + "'")
            db_conn.execute("Delete from orders where customerid = '" + str(customerid) + "'")
            dbr.append("Borramos el usuario y sus pedidos de manera incorrecta")

        else:
            time.sleep(duerme)
            dbr.append("Dormimos por " + str(duerme) + " segundos")

            # La transacción no falla. Borramos las orders asignadas al usuario y después el customerid
            db_conn.execute("Delete from orders where customerid = '" + str(customerid) + "'")
            db_conn.execute("Delete from customers where customerid = '" + str(customerid) + "'")
            dbr.append("Borramos el usuario y sus pedidos de manera correcta")

    except Exception as e:
        # Deshacer en caso de error
        # Comprobamos si hay que hacer deshacer la transacción con SQL o con SQLAlchemy
        if (bSQL):
            db_conn.execute("Rollback")
            dbr.append("Error en la transacción. La deshacemos con SQL")

        else:
            transaccion.rollback()
            dbr.append("Error en la transacción. La deshacemos con SQLAlchemy")

        # Desconexión de la base de datos
        db_conn.close()

    else:
        # Confirmar cambios si todo va bien
        # Comprobamos si hay que hacer commit de la transacción con SQL o con SQLAlchemy
        if (bSQL):
            db_conn.execute("Commit")
            dbr.append("Transacción realizada con éxito. La guardamos con SQL")

        else:
            transaccion.commit()
            dbr.append("Transacción realizada con éxito. La guardamos con SQLAlchemy")


    # Desconexión de la base de datos
    db_conn.close()
 
    return dbr
