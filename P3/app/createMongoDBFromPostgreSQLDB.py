# -*- coding: utf-8 -*-

import os
import sys, traceback
import pymongo
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

# Configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)

# Configurar mongodb
mongodb_engine = pymongo.MongoClient("mongodb://localhost:27017/")

# Creamos una base de datos en mongodb llamada si1 y una colección llamada topUSA
mongodb = mongodb_engine["si1"]
db_topUSA = mongodb["topUSA"]

try:
    # Conexión a la base de datos de postgres
    db_conn = None
    db_conn = db_engine.connect()

    topUSATable = "select imdb_movies.movieid, movietitle, year from imdb_movies, imdb_moviecountries\
                   where country = 'USA' and imdb_movies.movieid = imdb_moviecountries.movieid\
                   order by year desc\
                   limit 800"

    # Obtenemos las 800 películas estadounidenses más actuales de la base de datos Postgres
    movieList = list(db_conn.execute(topUSATable))
    recentUSAIds = list(db_conn.execute("select movieid from (" + topUSATable + ") as topUSATable"))

    moviesDocument = []
    moviesAnalized = 0
    print("Obteniendo los datos de las películas en Postgres y pasándolos a mongoDB...")

    # Conseguimos todos los datos de las 800 películas estadounidenses más actuales para pasarlos a mongoDB
    for movie in movieList:
        # Imprimemos en pantalla el estado de la ejecución
        moviesAnalized += 1
        print(str(moviesAnalized) + "/800")

        # Obtenemos el id, título, año, géneros, directores y actores de la película movie
        movieId = movie[0]
        movieTitle = movie[1]
        movieYear = movie[2]
        db_movieGenres = list(db_conn.execute("select genre from imdb_moviegenres\
                                               where movieid = '" + str(movieId) + "'"))
        movieGenres = []
        for genre in db_movieGenres:
            movieGenres.append(genre[0])

        db_movieDirectors = list(db_conn.execute("select directorname from imdb_directormovies, imdb_directors\
                                                  where movieid = '" + str(movieId) + "' and\
                                                  imdb_directormovies.directorid = imdb_directors.directorid"))
        movieDirectors = []
        for directorname in db_movieDirectors:
            movieDirectors.append(directorname[0])

        db_movieActors = list(db_conn.execute("select actorname from imdb_actormovies, imdb_actors\
                                               where movieid = '" + str(movieId) + "' and\
                                               imdb_actormovies.actorid = imdb_actors.actorid"))
        movieActors = []
        for actorname in db_movieActors:
            movieActors.append(actorname[0])

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

            categoryAffinity = 0

            # Revisamos cuántos género coinciden entre ambas películas para saber su afinidad
            for category in movieGenres:
                movieAppears = list(db_conn.execute("select movieid from imdb_moviegenres\
                                                     where genre = '" + category + "' and movieid = '" + str(movieid[0]) + "'"))

                # Si el género de la película coincide aumentamos el contador de afinidad
                if len(movieAppears) != 0:
                    categoryAffinity += 1

            # Si todas las categorías coinciden guardamos la película en la lista de más relacionadas
            if (categoryAffinity == len(movieGenres)):
                if (len(mostRelatedIds) < 10):
                    mostRelatedIds.append(movieid[0])                                           

            # Si la mitad de las categorías coinciden guardamos la película en la lista de relacionadas al 50%
            # Si la película tiene sólo un género, se indicarán sólo las películas más relacionadas
            elif (categoryAffinity == round(len(movieGenres) / 2) and len(movieGenres) != 1):
                if (len(relatedIds) < 10):
                    relatedIds.append(movieid[0])

            # Revisamos el número de coincidencias que hemos tenido hasta el momento, para parar cuando ya llevemos 10
            if len(mostRelatedIds) == 10 and (len(relatedIds) == 10 or len(movieGenres) == 1):
                break

        # Obtenemos los títulos y años de las películas más relacionadas
        mostRelatedMovies = []
        for mrmovieId in mostRelatedIds:
            db_mrmovie = list(db_conn.execute("select movietitle, year from (" + topUSATable + ") as topUSATable\
                                               where movieid = '" + str(mrmovieId) + "'"))[0]

            # Cambiamos el nombre de movietitle a title en el diccionario de la película
            mrmovie_dict = dict(db_mrmovie)
            mrmovie_dict["title"] = mrmovie_dict.pop("movietitle")
            mostRelatedMovies.append(mrmovie_dict)

        # Obtenemos los títulos y años de las películas relacionadas al 50%
        relatedMovies = []
        for rmovieId in relatedIds:
            db_rmovie = list(db_conn.execute("select movietitle, year from (" + topUSATable + ") as topUSATable\
                                              where movieid = '" + str(rmovieId) + "'"))[0]

            # Cambiamos el nombre de movietitle a title en el diccionario de la película
            rmovie_dict = dict(db_rmovie)
            rmovie_dict["title"] = rmovie_dict.pop("movietitle")
            relatedMovies.append(rmovie_dict)

        # Creamos y añadimos a la colección el documento para la película movie en mongoDB
        moviesDocument.append({
            'title': movieTitle,
            'genres': movieGenres,
            'year': movieYear,
            'directors': movieDirectors,
            'actors': movieActors,
            'most_related_movies': mostRelatedMovies,
            'related_movies': relatedMovies
        })

    # Insertamos las películas a mongodb
    db_topUSA.insert_many(moviesDocument)
    print("Películas insertadas a mongodb correctamente")

    # Desconectamos la base de datos de postgres
    db_conn.close()

except:
    # Control de errores en la base de datos
    if db_conn is not None:
        db_conn.close()
    print("Exception in DB access:")
    print("-"*60)
    traceback.print_exc(file=sys.stderr)
    print("-"*60)
