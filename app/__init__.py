# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 20:41:54 2021

@author: Alexandre Banon
"""

from flask import Flask

from .config import Config



# Initialisation et configuration de la session
app = Flask(__name__)
app.config.from_object(Config)


# Initialisation des chemins html
from app import routes