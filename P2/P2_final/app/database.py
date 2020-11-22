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

def db_listOfMovies1949():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Seleccionar las peliculas del anno 1949
        db_movies_1949 = select([db_table_movies]).where(text("year = '1949'"))
        db_result = db_conn.execute(db_movies_1949)
        #db_result = db_conn.execute("Select * from imdb_movies where year = '1949'")

        db_conn.close()

        return list(db_result)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_login(username, password):
    try:
        pass
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in login'

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

def db_register():
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

            # Calcular el precio medio de la película
            db_price = db_conn.execute("Select round (avg(price), 2) from products where movieid='" + str(movie_id) + "'")
            aux_price = list(db_price)[0]
            movie_price = aux_price[0]

            # Precio estándar en caso de que no se haya encontrado precio en la base de datos
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

            # Guardamos la información de la película en el catálogo
            data.append({
                'id': movie_id,
                'titulo': movie['movietitle'],
                'poster': movie['poster'],
                'precio': float(movie_price),
                'categoria': genres,
                'ano': movie['year'],
                'preview': movie['preview'],
                'sinopsis': "",
                'critica': "",
                'puntuacion': "-"
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
