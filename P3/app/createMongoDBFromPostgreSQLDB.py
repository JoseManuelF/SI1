# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_movies = Table('imdb_movies', db_meta, autoload=True, autoload_with=db_engine)

def db_topUsaMovies():
    try:
        # Conexión a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Obtenemos las 800 películas estadounidenses más actuales de la base de datos Postgres
        movieList = list(db_conn.execute("select imdb_movies.movieid, movietitle, year from imdb_movies, imdb_moviecountries\
                                          where country = 'USA' and imdb_movies.movieid = imdb_moviecountries.movieid\
                                          order by year desc\
                                          limit 800"))

        for movie in movieList:
            movieId = movie[0]
            movieGenres = list(db_conn.execute("select genre from imdb_moviegenres\
                                                where movieid = '" + str(movieId) + "';"))
            movieDirectors = list(db_conn.execute("select directorname from imdb_directormovies, imdb_directors\
                                                   where movieid = '" + str(movieId) + "' and\
                                                   imdb_directormovies.directorid = imdb_directors.directorid;"))
            print(movieDirectors)
        
        # Desconectamos la base de datos
        db_conn.close()

        #
        return movieList
    
    except:
        # Control de errores en la base de datos
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'ERROR in getTopVentas'

db_topUsaMovies()
