#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, make_response
import json
import os
import sys
import random
import hashlib

@app.route('/')
def home():
    print (url_for('static', filename='css/homeTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/loginTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return render_template('home.html', movies=catalogue['peliculas'])

@app.route('/movie_id_<int:id>')
def movie(id):
    print (url_for('static', filename='css/movieTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='css/main.css'), file=sys.stderr)

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

    return render_template('movie.html', movie=movie)

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
                session['usuario'] = request.form['uname']
                session.modified=True
                # se puede usar request.referrer para volver a la pagina desde la que se hizo login
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

        with open(datos_path, "w+") as f_datos:
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
        session.modified=True
        return redirect(url_for('home'))
    else:
        return render_template('register.html', user_exists="")
