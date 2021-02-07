# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 20:48:21 2021

@author: Alexandre Banon
"""

import os
import time
import random
import threading

from flask import render_template, request, Response

from tkinter import Tk
from tkinter.filedialog import askdirectory

from app import app
from photoloc.visualisation import create_map


# Contenus html pour l'ajout de base.html
HTML_BASE_TOP = """{% extends 'base.html' %}

{% block content %}

"""
HTML_BASE_BOTTOM = """
    
{% endblock %}
 
"""

# Variables du fichier de la carte
SAVING_PATH = os.path.join(app.root_path, app.template_folder)
RESULT_NAME = 'carte_geolocalisation_photos'
RESULT_FILE = RESULT_NAME+'.html'

EXPORTING_THREADS = {}



class ExportingThread(threading.Thread):
    def __init__(self, path):
        self.progress = 0
        self.path = path
        super().__init__()

    def run(self):
        for i in range(100):
            self.progress = 100 * i / ( 100 - 1 )
            print("{:.4}%\r".format(self.progress))
            time.sleep(0.1)
        """
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
                for line in f1:
                    f2.write(line)
                f2.write(HTML_BASE_BOTTOM)
                
        # On supprime l'ancienne carte
        os.remove(os.path.join(SAVING_PATH, RESULT_FILE))
        
        # On renomme le fichier temporaire par le nom de la carte
        os.rename(
            os.path.join(SAVING_PATH, 'tmp.html'), 
            os.path.join(SAVING_PATH, RESULT_FILE)
        )
        """
    
    

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
    Tk().withdraw()
    path = askdirectory()
    
    return render_template('index.html',
                           path=path,
                           progress=0)



@app.route('/result/', methods = ['GET'])
def display_map():

    if os.path.exists(os.path.join(SAVING_PATH, RESULT_FILE)):
        return render_template(RESULT_FILE)
    
    else:
        return render_template('carte_inconnue.html')
    


@app.route('/result/', methods = ['POST'])
def result():
    
    global EXPORTING_THREADS
    
    path = request.form['path']
    
    # Lance le script
    thread_id = random.randint(0, 10000)
    EXPORTING_THREADS[thread_id] = ExportingThread(path)
    EXPORTING_THREADS[thread_id].start()
    
    def generate_(thread):
        x = thread.progress
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = thread.progress
            
    def generate():
        x = 0
        while x <= 100:
            print('generator - '+str(x))
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(0.5)
    #return Response(generate(), mimetype= 'text/event-stream')
    
    return render_template('index.html',
                           path=path,
                           progress=0,
                           task_id=thread_id)
    
    
    #return 'task id: #%s' % thread_id


@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    global EXPORTING_THREADS

    return str(EXPORTING_THREADS[thread_id].progress)





# Gérer les erreurs
@app.errorhandler(404)
def err404(e):
    return render_template('404.html', err=e), 404


@app.errorhandler(500)
def not_found(e):
    return render_template('500.html', err=e), 500