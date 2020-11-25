# -*- coding: utf-8 -*-

import os
import sys, traceback
import json
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_movies = Table('imdb_movies', db_meta, autoload=True, autoload_with=db_engine)

def db_getTopVentas():
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Seleccionar las peliculas más vendidas en los últimos tres años
        db_result = db_conn.execute("Select * from getTopVentas(2018, 2020)")

        # Desconectamos la base de datos
        db_conn.close()

        # Devolvemos la lista de películas que nos da la función getTopVentas
        return list(db_result)
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in getTopVentas'

def db_register(usr, psw, email, card, saldo):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Cargamos el nombre de todos los demás usuarios
        db_users = db_conn.execute("Select username from customers")

        # Buscamos si el nombre de usuario ya está en uso
        if usr in list(db_users):
            # Desconectamos la base de datos
            db_conn.close()
            return False

        # Hallamos la customer id a incluir al nuevo usuario que se registra
        db_customerid = list(db_conn.execute("Select customerid from customers order by customerid desc limit 1"))[0]
        customerid = db_customerid[0] + 1
        
        # Creamos al nuevo usuario en la BBDD
        db_conn.execute("Insert into customers values('" + str(customerid) + "', '', '', '', '', '', '', '', '', '" + email + "', '', '', '" + card + "', '', '" + usr + "', '" + psw + "', '0', '" + str(saldo) + "', '', '1')")

        # Desconectamos la base de datos
        db_conn.close()

        # Devolvemos true, el usuario se ha registrado en la base de datos correctamente
        return True
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return False

def db_login(usr, psw):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Cogemos el username y la contraseña de la base de datos para el usuario con el nombre dado
        user = list(db_conn.execute("Select password from customers where '" + usr + "' = username"))

        # No hay ningún usuario con ese nombre, por lo que no está registrado en la base de datos
        if(len(user) <= 0):
            # Desconectamos la base de datos
            db_conn.close()
            return False

        # Conseguimos la contraseña dada por la conexión a la base de datos
        password = user[0][0]

        # Desconectamos la base de datos
        db_conn.close()

        # Si la contraseña coincide devolvemos True, si no, False
        if(password == psw):
            return True
        else:
            return False

    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return False

def db_saldo(usr):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        
        # Cogemos el saldo del usuario con el nombre dado y lo devolvemos
        saldo = db_conn.execute("Select income from customers where '" + usr + "' = username")

        # Desconectamos la base de datos
        db_conn.close()

        return int(list(saldo)[0][0])

    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 0

def db_update_saldo(usr, saldo):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Actualizamos el saldo del usuario en la tabla customers de la base de datos
        saldo = int(saldo)
        db_result = db_conn.execute("Update customers set income = '" + str(saldo) + "' where username = '" + usr + "'")

        # Desconectamos la base de datos
        db_conn.close()
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in update_saldo'

def update_catalogue():
    # Hallamos la ruta de la carpeta del catalogue
    this_dir = os.path.dirname(__file__)
    path = os.path.join(this_dir, "catalogue/catalogue.json")

    data = []

    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Conseguimos las películas propias que hemos metido a la base de datos
        db_movies = db_conn.execute("Select * from imdb_movies where movieid >= 800000")

        # Conseguimos las películas más vendidas de los tres últimos años
        moviesTopVentas = []
        for movie in db_getTopVentas():
            # Con el movie id incluimos a la lista todos los campos necesarios de la película
            selected_movie = db_conn.execute("Select * from imdb_movies where movieid='" + str(movie['id_']) + "'")
            moviesTopVentas = moviesTopVentas + list(selected_movie)

        # Concatenamos la lista de nuestra películas junto con las más vendidas de la base de datos
        movies_json = list(db_movies) + moviesTopVentas

        # Incluimos al catalogue.json las películas
        for movie in movies_json:
            movie_id = movie['movieid']

            # Conseguir el precio estándar de las películas (Standard)
            db_price = db_conn.execute("Select price from products where movieid='" + str(movie_id) + "' and description = 'Standard'")
            aux_price = list(db_price)[0]
            movie_price = aux_price[0]

            # Precio en caso de que no se haya encontrado precio en la base de datos
            if (movie_price == None):
                movie_price = 10.0

            # Hallamos los géneros de las películas
            db_genres = list(db_conn.execute("Select genre from imdb_moviegenres where movieid='" + str(movie_id) + "'"))

            # Guardamos las foreign keys de los géneros de las películas en una lista
            genres_id = []
            for g in db_genres:
                genres_id.append(g[0])

            # Hallamos el nombre de los géneros con las foreign keys
            genres = []
            for id in genres_id:
                genre_name = list(db_conn.execute("Select genre from genres where genreid='" + str(id) + "'"))

                # Guardamos el nombre de los géneros
                for name in genre_name:
                    genres.append(name[0])

            # Hallamos la puntuación de la película
            movie_puntuacion = movie['puntuacion']
            if (movie_puntuacion == None):
                # En caso de que no se haya encontrado puntuación a la película
                movie_puntuacion = '-'
            else:
                movie_puntuacion = float(movie_puntuacion)

            # Guardamos la información de la película en el catálogo
            data.append({
                'id': movie_id,
                'titulo': movie['movietitle'],
                'poster': movie['poster'],
                'precio': float(movie_price),
                'categoria': genres,
                'ano': movie['year'],
                'preview': movie['preview'],
                'sinopsis': movie['sinopsis'],
                'puntuacion': movie_puntuacion
            })

        # Desconectamos la base de datos
        db_conn.close()
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in update_catalog'

    # Accedemos al catalogue.json y lo actualizamos
    with open(path, 'w') as f_catalogue:
        json.dump(data, f_catalogue)

def db_update_categories():
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Seleccionar las categorías de la base de datos
        db_result = db_conn.execute("Select * from genres")

        # Desconectamos la base de datos
        db_conn.close()

        # Devolvemos la lista de películas que nos da la función getTopVentas
        return list(db_result)
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in update_categories' 

def db_add_order(usr):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Hallamos la order id a incluir a la tabla orders
        db_orderid = list(db_conn.execute("Select orderid from orders order by orderid desc limit 1"))[0]
        orderid = db_orderid[0] + 1

        # Hallamos el customer id del usuario que está haciendo una order
        db_customerid = list(db_conn.execute("Select customerid from customers where username = '" + usr + "'"))[0]
        customerid = db_customerid[0]

        # Creamos una nueva order con el orderid en la base de datos
        db_conn.execute("Insert into orders values ('" + str(orderid) + "', 'NOW()', '" + str(customerid) + "', '0', '10', '0', 'Processed')")

        # Desconectamos la base de datos
        db_conn.close()

        # Devolvemos la orderid para saber en qué order estamos operando
        return orderid
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 0

def db_get_order(usr):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Hallamos el customer id del usuario que recibe como argumento
        db_customerid = list(db_conn.execute("Select customerid from customers where username = '" + usr + "'"))[0]
        customerid = db_customerid[0]

        # Hallamos la order id del carrito del usuario
        db_orderid = list(db_conn.execute("Select orderid from orders where customerid = '" + str(customerid) + "' and status = 'Processed'"))
        if not db_orderid:
            return db_add_order(usr)

        # Desconectamos la base de datos
        db_conn.close()

        # Si tiene ya un carrito, cargamos ese
        return db_orderid[0][0]
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 0

def db_update_order(orderid, movieid, update):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Hallamos el prodid y el precio estándar de la película a tratar
        db_prodid = list(db_conn.execute("Select prod_id, price from products where movieid = '" + str(movieid) + "' and description = 'Standard'"))[0]
        prodid = db_prodid[0]
        price = db_prodid[1]

        # Conseguimos el quantity de la película de nuestra order en la base de datos
        db_quantity = list(db_conn.execute("Select quantity from orderdetail where orderid = '" + str(orderid) + "' and prod_id = '" + str(prodid) + "'"))

        # Comprobamos si hay que eliminar, actualizar o añadir la película al order
        if (update == 'Delete'):
            # Comprobamos si ya está la película en la order para eliminarla o actualizar el quantity
            if not db_quantity:
                # Borramos la película de la order con la orderid dada
                db_conn.execute("Delete from orderdetail where orderid = '" + str(orderid) + "' and prod_id = '" + str(prodid) + "'")
            
            else:
                quantity = db_quantity[0][0] - 1

                # Actualizamos el quantity y precio de la película de la order con la orderid dada
                db_conn.execute("Update orderdetail set price = (" + str(price) + " * " + str(quantity) + "), quantity = '" + str(quantity) + "' where orderid = '" + str(orderid) + "' and prod_id = '" + str(prodid) + "'")

        else:
            # Comprobamos si ya está la película en la order para insertarla como nueva o actualizar el quantity
            if not db_quantity:
                # Insertamos la película a la order con la orderid dada
                db_conn.execute("Insert into orderdetail values('" + str(orderid) + "', '" + str(prodid) + "', '" + str(price) + "', '1')")

            else:
                # Añadimos una película más a la order
                quantity = db_quantity[0][0] + 1

                # Actualizamos el quantity y precio de la película de la order con la orderid dada
                db_conn.execute("Update orderdetail set price = (" + str(price) + " * " + str(quantity) + "), quantity = '" + str(quantity) + "' where orderid = '" + str(orderid) + "' and prod_id = '" + str(prodid) + "'")

        # Desconectamos la base de datos
        db_conn.close()

    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in update_order'

def db_buy_order(orderid):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Actualizamos la tabla orders de la base de datos poniendo el estado en 'Pagado'
        # El trigger updInventory se encargará de actualizar el inventario
        db_conn.execute("Update orders set status = 'Paid' where orderid = '" + str(orderid) + "'")

        # Desconectamos la base de datos
        db_conn.close()

    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in buy_order'

def db_get_cesta(orderid):
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Conseguimos los prodid y quantity de las películas de la order dada por la orderid
        products = list(db_conn.execute("Select prod_id, quantity from orderdetail where orderid = '" + str(orderid) + "'"))

        # Lista de movie id de las películas de la order
        movies = []

        # Iteramos a través de todos los products de la order
        for p in products:
            prod_id = p[0]
            quantity = p[1]

            # Conseguimos el movie id del producto de la order
            movie_id = list(db_conn.execute("Select movieid from products where prod_id = '" + str(prod_id) + "'"))[0][0]

            # Añadimos tantas películas como nos marca la quantity
            for i in range(quantity):
                movies.append(movie_id)

        # Desconectamos la base de datos
        db_conn.close()
        return movies

    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in get_cesta'
