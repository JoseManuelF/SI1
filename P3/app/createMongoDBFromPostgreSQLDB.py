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

        topUSATable = "select imdb_movies.movieid, movietitle, year from imdb_movies, imdb_moviecountries\
                       where country = 'USA' and imdb_movies.movieid = imdb_moviecountries.movieid\
                       order by year desc\
                       limit 800"

        # Obtenemos las 800 películas estadounidenses más actuales de la base de datos Postgres
        movieList = list(db_conn.execute(topUSATable))

        for movie in movieList:
            # Obtenemos el id, título, año, géneros, directores y actores de la película movie
            movieId = movie[0]
            print(movieId)
            movieTitle = movie[1]
            movieYear = movie[2]
            movieGenres = list(db_conn.execute("select genre from imdb_moviegenres\
                                                where movieid = '" + str(movieId) + "'"))
            movieDirectors = list(db_conn.execute("select directorname from imdb_directormovies, imdb_directors\
                                                   where movieid = '" + str(movieId) + "' and\
                                                   imdb_directormovies.directorid = imdb_directors.directorid"))
            movieActors = list(db_conn.execute("select actorname from imdb_actormovies, imdb_actors\
                                                where movieid = '" + str(movieId) + "' and\
                                                imdb_actormovies.actorid = imdb_actors.actorid"))

            recentUSAIds = list(db_conn.execute("select movieid from (" + topUSATable + ") as topUSATable"))

            # Obtenemos hasta las 10 películas más actuales y más relacionadas (100%)
            mostRelatedIds = []
            # Obtenemos hasta las 10 películas más actuales y relacionadas al 50%
            relatedIds = []

            # Iteramos a través de las 800 películas para saber cuáles son las más relacionadas y las
            # relacionadas al 50% de la película movie
            for movieid in recentUSAIds:
                # Nos saltamos la misma película movie que estamos analizando
                if movieid[0] == movieId:
                    continue

                # El número de géneros de la película con la que lo vamos a comparar
                numGenres = list(db_conn.execute("select count(*) from imdb_moviegenres\
                                                  where movieid = '" + str(movieid[0]) + "'"))[0]

                categoryAffinity = 0

                # Revisamos que cada uno de los géneros coincida
                for category in movieGenres:
                    movieAppears = list(db_conn.execute("select movieid from imdb_moviegenres\
                                                         where genre = '" + category[0] + "' and movieid = '" + str(movieid[0]) + "'"))

                    # Si un género no coincide, descartamos la película como más relacionada
                    if len(movieAppears) != 0:
                        categoryAffinity += 1

                # Si todas las categorías coinciden guardamos la película en la lista de más relacionadas
                # En caso de que el número de géneros difiera, la descartamos
                if (categoryAffinity == len(movieGenres) and numGenres[0] == len(movieGenres)):
                    if (len(mostRelatedIds) < 10):
                        mostRelatedIds.append(movieid[0])

                # Si la mitad de las categorías coinciden guardamos la película en la lista de relacionadas al 50%
                # Si la película tiene sólo un género, se indicarán sólo las películas más relacionadas
                elif (categoryAffinity == round(len(movieGenres) / 2) and len(movieGenres) != 1):
                    if (len(relatedIds) < 10):
                        relatedIds.append(movieid[0])

                # Revisamos el número de coincidencias que hemos tenido hasta el momento, para parar cuando ya llevemos 10
                if len(mostRelatedIds) >= 10 and len(relatedIds) >= 10:
                    break

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
