# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:17:12 2021

@author: Alexandre Banon
"""

import sys
sys.path.append("..")

from app import app



if __name__ == '__main__':
    """Lancement de l'application flask.
    
    Exemples:
    ---------
    >>> !set FLASK_APP=site.py
    >>> !flask run -h '0.0.0.0' -p 8888 --cert=cert.pem --key=key.pem
    """
    
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8000,
        threaded=True
    )