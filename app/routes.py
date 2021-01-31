# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 20:48:21 2021

@author: Alexandre Banon
"""

import os

from flask import render_template, request

from tkinter import Tk
from tkinter.filedialog import askdirectory

from app import app
from photoloc.visualisation import create_map



@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html',
                           path='')



@app.route('/about/')
def about():
    return render_template('about.html')



@app.route('/directory/', methods = ['POST'])
def directory():
    
    # Initialise une boite de dialogue
    Tk().withdraw()
    path = askdirectory()
    
    return render_template('index.html',
                           path=path)



@app.route('/result/', methods = ['POST'])
def result():
    
    path = request.form['path']
    
    saving_path = os.path.join(app.root_path, app.template_folder)
    
    result_name='carte_geolocalisation_photos'
    create_map(
        pictures_path=path,
        saving_path=saving_path,
        result_name=result_name
    )
    
    return render_template(result_name+'.html')
    
    

# Gérer les erreurs

@app.errorhandler(404)
def err404(e):
    return render_template('404.html', err=e), 404


@app.errorhandler(500)
def not_found(e):
    return render_template('500.html', err=e), 500