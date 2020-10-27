#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, make_response
import json
import os
import sys
import random
import hashlib
import datetime

@app.route('/')
@app.route('/<category>')
@app.route('/login/<login>')
def home(category = None, login = False):
    print (url_for('static', filename='css/homeTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/loginTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    # Cargamos el catálogo de las películas
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    # Cargamos las categorías
    categories_data = open(os.path.join(app.root_path,'catalogue/categories.json'), encoding="utf-8").read()
    categories = json.loads(categories_data)

    # Si una categoría es None, significa que no hemos elegido categoría que filtrar.
    # Por lo que muestra todas las películas en el catalogue.json
    if(category == None):
        return render_template('home.html', movies=catalogue['peliculas'], categories=categories['categorias'], login=login)

    # Si una categoría ha sido especificada, la filtramos y solo mostramos
    # las películas que tengan esa categoría.
    else:
        print(category)
        categoryMovies = []
        for movie in catalogue['peliculas']:
            print(movie['título'] + ": ", end = "")
            if category in movie["categoria"]:
                print("V", end = "\n")
                categoryMovies.append(movie)
            else:
                print("x", end = "\n")
        return render_template('home.html', movies=categoryMovies, categories=categories['categorias'], login=login)

@app.route('/profile')
def profile():
    print (url_for('static', filename='css/homeTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/profileTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    # Si el usuario no ha iniciado sesión, te redirige a hacer login
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))

    # Hallamos la ruta de la carpeta de usuarios
    this_dir = os.path.dirname(__file__)
    previous_dir = os.path.dirname(this_dir)
    users_path = os.path.join(previous_dir, "usuarios/")

    # Accedemos al historial de la carpeta del usuario
    user_dir = os.path.join(users_path, "%s" %session['usuario'])
    historial_path = os.path.join(user_dir, "historial.json")
    
    # Cargamos el historial.json del usuario
    f = open(historial_path, "r")
    oldData = f.readline()

    if oldData == "":
        data = []
    else:
        data = json.loads(oldData)

    return render_template('profile.html', history=data)

@app.route('/sumar_saldo', methods=['GET', 'POST'])
def sumarSaldo():
    
    # Si el usuario no ha iniciado sesión, te redirige a hacer login
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))

    # Si el usuario tiene algún problema con el saldos en su sesión se cierra
    if 'saldo' not in session:
        return redirect(url_for('logout'))

    if request.method == 'POST':
        # Actualizamos el saldo de la sesión del usuario
        session['saldo'] = float(session['saldo']) + float(request.form['saldo'])

        # Hallamos la ruta de la carpeta de usuarios
        this_dir = os.path.dirname(__file__)
        previous_dir = os.path.dirname(this_dir)
        users_path = os.path.join(previous_dir, "usuarios/")

        # Accedemos a los datos de la carpeta del usuario
        user_dir = os.path.join(users_path, "%s" %session['usuario'])
        datos_path = os.path.join(user_dir, "datos.dat")

        # Cargamos los datos del perfil, para poder sobreescribir el saldo.
        segmented_data = []
        with open(datos_path, "r") as f_datos:
            segmented_data = f_datos.readline().split(" | ")
            
        # Actualizamos el saldo del usuario tras el ingreso.
        with open(datos_path, "w") as f_datos:
            data = ""
            for i in range(4):
                data += segmented_data[i] + " | "
            
            print("------------ Saldo: " + str(session['saldo']))
            data += str(session['saldo'])
            f_datos.write(data)

    return redirect(url_for('profile'))
    
@app.route('/movie_id_<int:id>')
def movie(id):
    print (url_for('static', filename='css/movieTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    # Cargamos el catálogo de las películas
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']

    # Buscamos la película dada por el id en el catálogo
    movie = None
    for item in movies:
        if item['id'] == id:
            movie = item.copy()

    # Si la película no existe te redirige a la página principal
    if (movie == None):
        return redirect(url_for('home'))

    # Si no existe, creamos una cesta con las películas en la sesión 
    if 'cesta' not in session:
        session['cesta'] = []

    # Vemos cuántas veces la película ya ha sido añadida a la cesta
    added = 0
    for m in session['cesta']:
        if m['id'] == id:
            added += 1
            
    return render_template('movie.html', movie=movie, added=added)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Hallamos la ruta de la carpeta de usuarios
        this_dir = os.path.dirname(__file__)
        previous_dir = os.path.dirname(this_dir)
        users_path = os.path.join(previous_dir, "usuarios/")

        # Comprobamos si el usuario dado está registrado
        users_list = os.listdir(users_path)
        for u in users_list:
            if request.form['uname'] == u:
                # Accedemos a los datos de la carpeta del usuario
                user_dir = os.path.join(users_path, "%s" %u)
                datos_path = os.path.join(user_dir, "datos.dat")

                # Comprobamos si la hash password coincide con la dada en el login
                login_password = request.form['psw']
                with open(datos_path, "r+") as f_datos:
                    # Hasheamos la contraseña dada en el login
                    hash_login = hashlib.sha512(("%s" %login_password).encode('utf-8')).hexdigest()

                    # Vemos si las contraseñas son iguales
                    line = f_datos.readline()
                    if hash_login == line.split(" | ")[1]:
                        session['usuario'] = request.form['uname']
                        session['saldo'] = line.split(" | ")[4]
                        session.modified=True
                        return redirect(url_for('home'))
                    else:
                        return redirect(url_for('home'))

        # El usuario no está registrado en la carpeta de usuarios
        return redirect(url_for('register'))
    else:
        # se puede guardar la pagina desde la que se invoca 
        session['url_origen']=request.referrer
        session.modified=True
        
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return redirect(url_for('home'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('saldo', None)
    session.pop('usuario', None)
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

        # Hallamos la ruta de la carpeta de usuarios
        this_dir = os.path.dirname(__file__)
        previous_dir = os.path.dirname(this_dir)
        users_path = os.path.join(previous_dir, "usuarios/")

        # Vemos si el usuario ya existe
        users_list = os.listdir(users_path)
        for u in users_list:
            if (u == username):
                # El usuario ya existe
                user_exists = "El usuario dado está ya en uso. Intente otro por favor."
                return render_template('register.html', user_exists=user_exists)

        # El usuario no existe. Creamos una nueva carpeta del usuario
        user_dir = os.path.join(users_path, "%s" %username)
        os.mkdir(user_dir)
        os.chmod(user_dir, 0o777) # Permisos para leer/escribir/ejecutar en la carpeta

        # Creamos datos.dat e historial.json en la carpeta del usuario
        datos_path = os.path.join(user_dir, "datos.dat")
        historial_path = os.path.join(user_dir, "historial.json")

        saldo = 0
        with open(datos_path, "w") as f_datos:
            # Hasheamos la contraseña
            hash_password = hashlib.sha512(("%s" %password).encode('utf-8')).hexdigest()

            # Asignamos al saldo inicial un valor random entre 0 y 100
            saldo = random.randint(0, 100)

            # Incluimos la info del usuario en los datos
            f_datos.write(username + ' | ' + hash_password + ' | ' + email + ' | ' + card + ' | ' + str(saldo))

        with open(historial_path, "x") as f_hist:
            pass

        # Registración completa. Volver a la página principal ya con la sesión iniciada
        session['usuario'] = request.form['uname']
        session['saldo'] = saldo
        session.modified=True
        return redirect(url_for('home'))
    else:
        return render_template('register.html', user_exists="")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Cargamos el catálogo de las películas
        catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
        catalogue = json.loads(catalogue_data)

        # Cargamos las categorías
        categories_data = open(os.path.join(app.root_path,'catalogue/categories.json'), encoding="utf-8").read()
        categories = json.loads(categories_data)

        search = request.form['search']
        # Si la búsqueda no es una cadena vacía, eso significa que estamos buscando algo.
        if(search != ""):
            print("Looking for: " + search)
            searchMovies = []
            for movie in catalogue['peliculas']:
                print(movie['título'] + ": ", end = "")
                if search.lower() in movie["título"].lower():
                    print("V", end = "\n")
                    searchMovies.append(movie)
                else:
                    print("x", end = "\n")
            return render_template('home.html', movies=searchMovies, categories=categories['categorias'])

        else:
            return redirect(url_for('home'))

    else:
        return redirect(url_for('home'))

@app.route('/cesta')
@app.route('/cesta_add/<int:add>')
@app.route('/cesta_delete/<int:delete>')
def cesta(add = None, delete = None):
    # Cargamos el catálogo de las películas
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

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
        return redirect(url_for('cesta'))

    # Tenemos como argumento el id de la película a añadir a la cesta
    elif add != None:
        # Buscamos la película dada por el id en el catálogo
        for item in catalogue['peliculas']:
            if item['id'] == add:
                movie = item.copy()

        # Añadimos a la cesta de la sesión la película
        session['cesta'].append(movie)
        session.modified = True
        return redirect(url_for('movie', id=add))
        
    # No hay argumentos, accedemos a la cesta
    else:
        # Calculamos el precio total de la cesta
        precio = 0.0
        for pritem in session['cesta']:
            for prcatalog in catalogue['peliculas']:
                if pritem['id'] == prcatalog['id']:
                    precio += prcatalog['precio']

        return render_template('cesta.html', cesta=session['cesta'], precio=precio)

@app.route('/buy')
def buy():
    # Si no existe, creamos una cesta con las películas en la sesión
    if 'cesta' not in session:
        session['cesta'] = []

    # Cargamos el catálogo de las películas
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    # Calculamos el precio total de la cesta
    precio = 0.0
    for pritem in session['cesta']:
        for prcatalog in catalogue['peliculas']:
            if pritem['id'] == prcatalog['id']:
                precio += prcatalog['precio']

    # El usuario no ha iniciado sesión, por lo que no podrá comprar las películas
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))
    else:
        # Hallamos la ruta de la carpeta de usuarios
        this_dir = os.path.dirname(__file__)
        previous_dir = os.path.dirname(this_dir)
        users_path = os.path.join(previous_dir, "usuarios/")

        # Accedemos a los datos de la carpeta del usuario
        user_dir = os.path.join(users_path, "%s" %session['usuario'])
        datos_path = os.path.join(user_dir, "datos.dat")

        saldo = 0.0
        segmented_data = []
        # Vemos si el saldo del usuario es suficiente para comprar las películas
        with open(datos_path, "r") as f_datos:
            segmented_data = f_datos.readline().split(" | ")
            saldo = float(segmented_data[4])

            # Descontamos el precio total al saldo
            saldo = saldo - precio

        # No hay saldo suficiente
        if saldo < 0.0:
            return redirect(url_for('profile'))
            
        else:
            # Actualizamos el saldo del usuario tras la compra
            session['saldo'] = saldo
            with open(datos_path, "w") as f_datos:
                data = ""
                for i in range(4):
                    data += segmented_data[i] + " | "
                
                data += str(saldo)
                f_datos.write(data)
            
            # Añadir las películas compradas al historial.json
            historial_path = os.path.join(user_dir, "historial.json")
            printJson(historial_path, session['cesta'])

            # Borrar la cesta
            session.pop('cesta', None)

            return redirect(url_for('home'))

@app.route('/buy_direct/<int:id>')
def buy_direct(id = 0):
    # Cargamos el catálogo de las películas
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']

    # Buscamos la película dada por el id en el catálogo
    movie = None
    for item in movies:
        if item['id'] == id:
            movie = item.copy()

    # Si la película no existe te redirige a la página principal
    if (movie == None):
        return redirect(url_for('home'))

    # Hallamos el precio de la película
    precio = movie['precio']

    # El usuario no ha iniciado sesión, por lo que no podrá comprar las películas
    if 'usuario' not in session:
        return redirect(url_for('home', login=True))
    else:
        # Hallamos la ruta de la carpeta de usuarios
        this_dir = os.path.dirname(__file__)
        previous_dir = os.path.dirname(this_dir)
        users_path = os.path.join(previous_dir, "usuarios/")

        # Accedemos a los datos de la carpeta del usuario
        user_dir = os.path.join(users_path, "%s" %session['usuario'])
        datos_path = os.path.join(user_dir, "datos.dat")

        saldo = 0.0
        segmented_data = []
        # Vemos si el saldo del usuario es suficiente para comprar la película
        with open(datos_path, "r") as f_datos:
            segmented_data = f_datos.readline().split(" | ")
            saldo = float(segmented_data[4])

            # Descontamos el precio total al saldo
            saldo = saldo - precio

        # No hay saldo suficiente
        if saldo < 0.0:
            return redirect(url_for('profile'))
            
        else:
            # Actualizamos el saldo del usuario tras la compra
            session['saldo'] = saldo
            with open(datos_path, "w") as f_datos:
                data = ""
                for i in range(4):
                    data += segmented_data[i] + " | "
                
                data += str(saldo)
                f_datos.write(data)
            
            # Añadir la película comprada al historial.json
            historial_path = os.path.join(user_dir, "historial.json")

            movieList = []
            movieList.append(movie)
            printJson(historial_path, movieList)

            return redirect(url_for('home'))

# Función auxiliar para imprimir el historial.json del usuario
def printJson(path, movies):
    # Hallamos la fecha en la que se compraron las películas
    dt = datetime.datetime.today()

    f = open(path, "r")
    oldData = f.readline()

    if oldData == "":
        data = []
    else:
        data = json.loads(oldData)
    f.close()

    # Incluimos los detalles de las películas compradas
    for movie in movies:
        data.append({
            'titulo': movie["título"],
            'precio': movie["precio"],
            'fecha': str(dt.day) + "/" + str(dt.month) + "/" + str(dt.year)
        })

    # Accedemos al historial.json del usuario y lo actualizamos
    with open(path, 'w') as f_historial:
        json.dump(data, f_historial)
