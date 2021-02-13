# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 20:48:21 2021

@author: Alexandre Banon
"""

import os
import threading

from flask import render_template, request, jsonify

from tkinter import Tk
from tkinter.filedialog import askdirectory

from app import app
from photoloc.visualisation import create_map


# Contenus html pour l'ajout de base.html
HTML_BASE_TOP = """{% extends 'base.html' %}

{% block content %}

<!DOCTYPE html>
<head>    
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    
        <script>
            L_NO_TOUCH = false;
            L_DISABLE_3D = false;
        </script>
    
    <style>html, body {width: 100%;height: 100%;margin: 0;padding: 0;}</style>
    <style>#map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.js"></script>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.css"/>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css"/>
    
"""
HTML_BASE_BOTTOM = """
    
{% endblock %}
 
"""

# Variables du fichier de la carte
SAVING_PATH = os.path.join(app.root_path, app.template_folder)
RESULT_NAME = 'carte_geolocalisation_photos'
RESULT_FILE = RESULT_NAME+'.html'

EXPORTING_THREAD = None



class ExportingThread(threading.Thread):
    def __init__(self, path):
        self.progress = 0
        self.path = path
        super().__init__()

    def run(self):
        
        # Lance le script
        create_map(
            pictures_path = self.path,
            saving_path   = SAVING_PATH,
            result_name   = RESULT_NAME,
            thread        = self
        )
        
        # On rajoute le html de base à la carte créée
        with open(os.path.join(SAVING_PATH, RESULT_FILE)) as f1:
            with open(os.path.join(SAVING_PATH, 'tmp.html'), "w") as f2:
                f2.write(HTML_BASE_TOP)
                i = 0
                for line in f1:
                    if i>21:
                        f2.write(line)
                    i += 1
                f2.write(HTML_BASE_BOTTOM)
                
        # On supprime l'ancienne carte
        os.remove(os.path.join(SAVING_PATH, RESULT_FILE))
        
        # On renomme le fichier temporaire par le nom de la carte
        os.rename(
            os.path.join(SAVING_PATH, 'tmp.html'), 
            os.path.join(SAVING_PATH, RESULT_FILE)
        )
        
        # On termine la progression
        self.progress = 100
        
    
    

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')



@app.route('/about/')
def about():
    return render_template('about.html')



@app.route('/directory/', methods = ['POST'])
def directory():
    
    # Initialise une boite de dialogue
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    path = askdirectory()
    
    return render_template('index.html',
                           path=path)



@app.route('/result/', methods = ['GET'])
def display_map():

    if os.path.exists(os.path.join(SAVING_PATH, RESULT_FILE)):
        return render_template(RESULT_FILE)
    
    else:
        return render_template('carte_inconnue.html')
    


@app.route('/result/', methods = ['POST'])
def result():
    
    global EXPORTING_THREAD
    
    path = request.form['path']
    
    # Lance le script
    EXPORTING_THREAD = ExportingThread(path)
    EXPORTING_THREAD.start()
            
    if request.method == 'POST':
        msg = 'La carte a bien été créée !'    
    return jsonify(msg)



@app.route('/progress/<int:thread_id>', methods = ["POST","GET"])
def progress(thread_id):
    global EXPORTING_THREAD
    
    msg = str(EXPORTING_THREAD.progress)

    return jsonify(msg)



# Gérer les erreurs
@app.errorhandler(404)
def err404(e):
    return render_template('404.html', err=e), 404


@app.errorhandler(500)
def not_found(e):
    return render_template('500.html', err=e), 500