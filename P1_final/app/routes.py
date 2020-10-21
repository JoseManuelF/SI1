#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, make_response
import json
import os
import sys

@app.route("/setcookie/<user>")
def setcookie(user):
    msg = "usercookie set to: " + user
    response = make_response(render_template('mensaje.html', mensaje=msg))
    response.set_cookie('helloflask_user',user)
    return response

@app.route("/getcookie")
def getcookie():
    user_id= request.cookies.get('helloflask_user')
    if user_id:
        msg= "useris: " + user_id
    else:
        msg= "no usercookie"
    return render_template('mensaje.html', mensaje=msg)

@app.route('/')
def home():
    '''
    print (url_for('static', filename='homeTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='loginTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='main.css'), file=sys.stderr) '''
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    return render_template('home.html', movies=catalogue['peliculas'])

@app.route('/<id>')
def movie(id):
    '''
    print (url_for('static', filename='movieTemplate.css'), file=sys.stderr)
    print (url_for('static', filename='main.css'), file=sys.stderr) '''

    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    movies=catalogue['peliculas']

    movie = None
    for item in movies:
        if item['id'] == int(id):
            movie = item.copy()

    return render_template('movie.html', movie=movie)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if 'uname' in request.form:
        # aqui se deberia validar con fichero .dat del usuario
        if request.form['uname'] == 'pp':
            session['usuario'] = request.form['uname']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('home'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return redirect(url_for('register'))
    else:
        # se puede guardar la pagina desde la que se invoca 
        session['url_origen']=request.referrer
        session.modified=True        
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('home.html', title = "Sign In")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')
