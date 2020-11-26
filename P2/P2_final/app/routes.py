#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
from flask import render_template, request, url_for, redirect, session, make_response
import json
import os
import sys
import random
import hashlib
import datetime

# Actualizamos el catalogue.json con películas de la base de datos
database.update_catalogue()

# Cargamos el catálogo de las películas
catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
catalogue = json.loads(catalogue_data)

# Cargamos las categorías de la base de datos
categories = database.db_update_categories()

@app.route('/')
@app.route('/<category>')
@app.route('/login_<login>')
@app.route('/login_error:<login_error>')
def home(category = None, login = False, login_error = ""):
    print (url_for('static', filename='css/homeTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/loginTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    # Si una categoría es None, significa que no hemos elegido categoría que filtrar.
    # Por lo que muestra todas las películas en el catalogue.json
    if(category == None):
        return render_template('home.html', movies=catalogue,
                               categories=categories, login=login, login_error=login_error)

    # Si una categoría ha sido especificada, la filtramos y solo mostramos
    # las películas que tengan esa categoría.
    else:
        print(category)
        categoryMovies = []
        for movie in catalogue:
            print(movie['titulo'] + ": ", end = "")
            if category in movie["categoria"]:
                print("V", end = "\n")
                categoryMovies.append(movie)
            else:
                print("x", end = "\n")
        return render_template('home.html', movies=categoryMovies,
                               categories=categories, login=login, login_error=login_error)

@app.route('/profile')
def profile():
    print (url_for('static', filename='css/homeTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/profileTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    # Si el usuario no ha iniciado sesión, te redirige a hacer login
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))
    
    # Accedemos a la base de datos para ver los id de las películas compradas por el usuario logeado,
    # junto con las fechas de la compras
    aux = database.db_get_history(session['usuario'])
    history_moviesid = aux[0]
    history_fecha = aux[1]

    # Buscamos las películas dadas por el history_moviesid y history_fecha en el catálogo
    data = []
    for item in catalogue:
        for movieid, date in zip(history_moviesid, history_fecha):
            if item['id'] == movieid:
                movie = item.copy()
                movie['fecha'] = date
                data.append(movie)

    # Conseguimos el saldo del usuario en la base de datos
    saldo = database.db_saldo(session['usuario'])

    return render_template('profile.html', history=data, categories=categories, saldo=saldo)

@app.route('/sumar_saldo', methods=['GET', 'POST'])
def sumarSaldo():
    # Si el usuario no ha iniciado sesión, te redirige a hacer login
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))

    if request.method == 'POST':
        # Conseguimos el saldo del usuario en la base de datos
        saldo = database.db_saldo(session['usuario'])

        # Calculamos el resultado de la suma del saldo
        suma_saldo = round(float(saldo) + float(request.form['saldo']), 2)

        # Accedemos a la base de datos para actualizar el saldo del usuario tras el ingreso
        database.db_update_saldo(session['usuario'], suma_saldo)

    return redirect(url_for('profile'))
    
@app.route('/movie_id_<int:id>')
def movie(id):
    print (url_for('static', filename='css/movieTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    # Cargamos el catálogo de las películas
    movies=catalogue

    # Buscamos la película dada por el id en el catálogo
    movie = None
    for item in movies:
        if item['id'] == id:
            movie = item.copy()

    # Si la película no existe te redirige a la página principal
    if (movie == None):
        return redirect(url_for('home'))

    # Si el usuario está logeado accedemos a través de la base de datos, sino a través de la sesión
    if 'usuario' not in session:
        # Si no existe, creamos una cesta con las películas en la sesión 
        if 'cesta' not in session:
            session['cesta'] = []

        # Vemos cuántas veces la película ya ha sido añadida a la cesta
        added = 0
        for m in session['cesta']:
            if m['id'] == id:
                added += 1
    
    else:
        # Vemos cuántas veces la película ya ha sido añadida a la cesta en la base de datos
        added = 0
        cesta = database.db_get_cesta(session['order'])
        for m in cesta:
            if m == id:
                added += 1

    return render_template('movie.html', movie=movie, added=added, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Mensaje de error en caso de que no se pueda iniciar sesión
        login_error = "El nombre de usuario o la contraseña no coinciden."

        # Llamamos a la función login de la database que devuelve false si
        # el usuario no está registrado o true en caso contrario
        if (database.db_login(request.form['uname'], request.form['psw']) == False):
            # El usuario no está registrado en la base de datos
            return redirect(url_for('home', login_error=login_error))

        # El usuario está registrado en la base de datos, se inicia sesión
        session['usuario'] = request.form['uname']

        # Llamamos a la función get_order para conseguir una order de la base de datos conforme al usuario
        orderid = database.db_get_order(session['usuario'])

        # Guardamos la orderid dada por la base de datos a la sesión
        session['order'] = orderid
        
        # Si no existe, creamos una cesta con las películas en la sesión
        if 'cesta' not in session:
            session['cesta'] = []

        # Añadimos a la order en la base de datos las películas que estaban en el carrito
        for movie in session['cesta']:
            database.db_update_order(orderid, movie['id'], 'Insert')
        session.pop('cesta', None)

        session.modified=True
        return redirect(url_for('home'))
    else:
        # se puede guardar la página desde la que se invoca 
        session['url_origen']=request.referrer
        session.modified=True
        
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return redirect(url_for('home', login=True))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('cesta', None)
    session.pop('usuario', None)
    session.pop('order', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    print (url_for('static', filename='css/registerTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    if request.method == 'POST':
        # Conseguimos los valores metidos al registrarse
        username = request.form['uname']
        email = request.form['email']
        password = request.form['psw']
        card = request.form['tarjeta']

        # Asignamos al saldo inicial del usuario que se registra un valor random entre 0 y 100
        saldo = random.randint(0, 100)

        # Llamamos a la función register de la database que devuelve false si
        # ya existe el nombre de usuario o te lo añade a la base de datos en caso contrario  
        if (database.db_register(username, password, email, card, saldo) == False):
            # El usuario ya existe
            user_exists = "El usuario dado está ya en uso. Intente otro por favor."
            return render_template('register.html', user_exists=user_exists)

        # Registración completa. Volver a la página principal ya con la sesión iniciada
        session['usuario'] = request.form['uname']

        # Llamamos a la función get_order para conseguir una order de la base de datos conforme al usuario
        orderid = database.db_get_order(session['usuario'])

        # Guardamos la orderid dada por la base de datos a la sesión
        session['order'] = orderid

        # Añadimos a la order en la base de datos las películas que estaban en el carrito
        for movie in session['cesta']:
            database.db_update_order(orderid, movie['id'], 'Insert')
        session.pop('cesta', None)

        session.modified=True
        return redirect(url_for('home'))
    else:
        return render_template('register.html', user_exists="")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':

        search = request.form['search']
        # Si la búsqueda no es una cadena vacía, eso significa que estamos buscando algo.
        if(search != ""):
            print("Looking for: " + search)
            searchMovies = []
            for movie in catalogue:
                print(movie['titulo'] + ": ", end = "")
                if search.lower() in movie["titulo"].lower():
                    print("V", end = "\n")
                    searchMovies.append(movie)
                else:
                    print("x", end = "\n")
            return render_template('home.html', movies=searchMovies, categories=categories)

        else:
            return redirect(url_for('home'))

    else:
        return redirect(url_for('home'))

@app.route('/cesta')
@app.route('/cesta_add/<int:add>')
@app.route('/cesta_delete/<int:delete>')
def cesta(add = None, delete = None):
    # Si no existe, creamos una cesta con las películas en la sesión
    if 'cesta' not in session:
        session['cesta'] = []

    # Tenemos como argumento el id de la película a eliminar de la cesta
    if delete != None:
        for item in session['cesta']:
            if item['id'] == delete:
                # Eliminamos de la cesta la película
                session['cesta'].remove(item)
                session.modified = True
                break

        # Si un usuario ha iniciado sesión actualizamos la base de datos
        if 'usuario' in session:
            # Llamamos a la función update_order para eliminar la película de la order en la base de datos
            database.db_update_order(session['order'], delete, 'Delete')

        return redirect(url_for('cesta'))

    # Tenemos como argumento el id de la película a añadir a la cesta
    elif add != None:
        # Buscamos la película dada por el id en el catálogo
        for item in catalogue:
            if item['id'] == add:
                movie = item.copy()

        # Añadimos a la cesta de la sesión la película
        session['cesta'].append(movie)
        session.modified = True

        # Si un usuario ha iniciado sesión actualizamos la base de datos
        if 'usuario' in session:
            # Llamamos a la función update_order para añadir una película a la order en la base de datos
            database.db_update_order(session['order'], add, 'Insert')

        return redirect(url_for('movie', id=add))
        
    # No hay argumentos, accedemos a la cesta
    else: 
        # Calculamos el precio total de la cesta
        precio = 0.0
        for pritem in session['cesta']:
            for prcatalog in catalogue:
                if pritem['id'] == prcatalog['id']:
                    precio = round((precio + prcatalog['precio']), 2)

        if 'usuario' in session:
            movies = []
            for movieid in database.db_get_cesta(session['order']):
                for prcatalog in catalogue:
                    if movieid == prcatalog['id']:
                        movies.append(prcatalog)

            # Llamamos a la función order_price de la base de datos para hallar el precio total de la cesta
            precio = database.db_order_price(session['order'])

            # Conseguimos el saldo del usuario en la base de datos
            saldo = database.db_saldo(session['usuario'])

            return render_template('cesta.html', cesta=movies, precio=precio, categories=categories, saldo=saldo)

        return render_template('cesta.html', cesta=session['cesta'], precio=precio, categories=categories)

@app.route('/buy')
def buy():
    # El usuario no ha iniciado sesión, por lo que no podrá comprar las películas
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))
    else:
        # Llamamos a la función order_price de la base de datos para hallar el precio total de la cesta
        precio = database.db_order_price(session['order'])

        # Conseguimos el saldo del usuario en la base de datos
        saldo = database.db_saldo(session['usuario'])

        # Descontamos el precio total al saldo
        saldo = round((saldo - precio), 2)

        # No hay saldo suficiente
        if saldo < 0.0:
            return redirect(url_for('profile'))

        else:
            # Actualizamos el saldo del usuario tras la compra
            database.db_update_saldo(session['usuario'], saldo)

            # Actualizamos la tabla orders de la base de datos poniendo el estado en 'Pagado'
            database.db_buy_order(session['order'])

            # Borrar la cesta
            session.pop('order', None)

            # Creamos una cesta nueva
            session['order'] = database.db_get_order(session['usuario'])
            session.modified=True

            return redirect(url_for('home'))

@app.route('/buy_direct/<int:id>')
def buy_direct(id = 0):
    # Cargamos el catálogo de las películas
    movies=catalogue

    # Buscamos la película dada por el id en el catálogo
    movie = None
    for item in movies:
        if item['id'] == id:
            movie = item.copy()

    # Si la película no existe te redirige a la página principal
    if (movie == None):
        return redirect(url_for('home'))

    # El usuario no ha iniciado sesión, por lo que no podrá comprar las películas
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))
    else:
        # Añadimos la compra de la película a la base de datos
        orderid = database.db_add_order(session['usuario'])
        database.db_update_order(orderid, id, 'Insert')

        # Llamamos a la función order_price de la base de datos para hallar el precio con impuestos de la película
        precio = database.db_order_price(orderid)

        # Conseguimos el saldo del usuario en la base de datos
        saldo = database.db_saldo(session['usuario'])

        # Descontamos el precio total al saldo
        saldo = round((saldo - precio), 2)

        # No hay saldo suficiente
        if saldo < 0.0:
            # Borramos la fallida compra de la base de datos
            database.db_delete_order(orderid)

            return redirect(url_for('profile'))

        else:
            # Actualizamos el saldo del usuario tras la compra
            database.db_update_saldo(session['usuario'], saldo)

            # Actualizamos la tabla orders de la base de datos poniendo el estado en 'Pagado'
            database.db_buy_order(orderid)

            return redirect(url_for('home'))

@app.route('/movieOfTheDay')
def movieOfTheDay():
    dt = datetime.datetime.today()
    
    # Pseudo random generator (0, número de películas en el catálogo - 1)
    movie_pos = ((dt.day*31 + dt.month*17 + dt.year*29) % len(catalogue))

    # Hallamos el id de la película en la posición random dentro del catálogo
    today_movie = catalogue[movie_pos]
    movie_id = today_movie['id']

    return redirect(url_for('movie', id=movie_id))
