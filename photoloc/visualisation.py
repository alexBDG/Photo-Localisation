# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 19:14:15 2021

@author: Alexandre
"""

import os
import time
import base64
import folium
import pandas as pd

from PIL import Image
from tqdm import tqdm
from folium import IFrame
from folium.plugins import MarkerCluster

from .extraction import get_dataset



class Environment:
    """Création de divers variables pour gérer chemins de résultats.

    Parameters
    ----------
    save_name : str, default='carte_geolocalisation_photos'
        Nom du fichier de résultat (pas besoin de rajoute l'extension).
                                    
    saving_path : str or None, default=None
        Nom du dossier d'enregistrement de la carte. Si non renseigné, la carte
        sera enregistrée par défaut dans le dossier `'results'`.
    """
    
    def __init__(self, 
                 save_name='carte_geolocalisation_photos',
                 saving_path=None):
        # Dossier de résultats
        self.tmp_dir = r"results"
        
        # Dossier de résultats
        self.result_dir = self.tmp_dir if saving_path is None else saving_path
        
        # Nom du fichier temporaire
        self.tmp_path = os.path.join(self.result_dir, 'tmp.png')
        
        # Création du dossier temporaire
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
            
        # Nom du fichier de résultat
        self.result_path = os.path.join(
            self.result_dir, save_name+'.html'
        )
            
            
            
    def clean(self):
        """Supprime les fichiers temporaires.
        """
        # On supprime les fichiers temporaires
        os.remove(self.tmp_path)



def add_markers(m, data, env, width=300, thread=None):
    """Ajoute un marqueur sur la carte. Chaque marqueur est placé à l'endroit
    où la photo a été prise, et une miniature est ajoutée lorsque l'utilisateur
    clic dessus.

    Parameters
    ----------
    m : Map
        Planisphère, object de la bibliothèque `folium`.
        
    data : DataFrame
        Données contenant les informations de chaque photo à ajouter.
        
    env : Object
        Chemins d'accès.
        
    width : int, default=300
        Taille des miniatures d'images.
        
    thread : threading object or None, default=None
        Thread executant cette fonction dans le cas de déploiement web.

    Returns
    -------
    m : Map
        Planisphère, object de la bibliothèque `folium`.
    """
    
    print("Création de la carte ...")
    time.sleep(0.2)
    
    # Création d'un object de regroupement de points d'intérêts
    marker_cluster = MarkerCluster().add_to(m)

    # Balise html pour l'affichage Popup d'une image
    html = '<img src="data:image/png;base64,{0}">'.format

    for i in tqdm(range(len(data))):
        
        if thread is not None:
            # (len(data) - 1) --> en principe
            # Mais on veut que pour arriver à 100%, l'écriture du fichier soit
            # finie
            thread.progress = 100 * i / ( len(data) )

        # Redimentionnement de l'image et enregistrement temporaire
        img = Image.open(data.iloc[i]['path'])
        height = int(img.size[1]*(width/img.size[0]))
        img = img.resize((width, height), Image.ANTIALIAS)
        if int(data.iloc[i]['orientation'])>1:
            img = img.transpose(Image.ROTATE_270)
            w, h = height, width
        else:
            w, h = width, height
        img.save(env.tmp_path)
        del img

        # Longitude / Latitude
        lat, lon = data.iloc[i]['lat'], data.iloc[i]['lon']

        # On ouvre l'image temporaire et on l'encode
        encoded = base64.b64encode(open(env.tmp_path, 'rb').read())

        # On en fait une Frame puis un Popup
        iframe = IFrame(
            html(encoded.decode('UTF-8'), w, h), width=w+20, height=h+20
        )
        popup = folium.Popup(iframe, max_width=2650)

        # On choisit l'icône
        icon = folium.Icon(icon="camera", prefix="fa")

        # On ajoute le Marker
        marker = folium.Marker([lat, lon], popup=popup, icon=icon)
        marker.add_to(marker_cluster)
    
    # Nettoyage
    env.clean()
    
    return m



def create_map(pictures_path=r"C:\\Users\\alspe\\Pictures\\2020\\06-2020",
               result_name='carte_geolocalisation_photos',
               saving_path=None,
               thread=None):
    """Crée une projection géographique dans laquelle des images sont ajoutées
    selon leur données de géolocalisation.

    Parameters
    ----------
    pictures_path : str, default=r"C:\\Users\\alspe\\Pictures\\2020\\06-2020"
        Chemin vers le dossier d'images.
                                    
    saving_path : str or None, default=None
        Nom du dossier d'enregistrement de la carte. Si non renseigné, la carte
        sera enregistrée par défaut dans le dossier `'results'`.
        
    thread : threading object or None, default=None
        Thread executant cette fonction dans le cas de déploiement web.
    """
    
    # Info
    start = time.time()
    print('Début du script')
    
    # Création de l'environnement
    env = Environment(result_name, saving_path=saving_path)
    
    # On crée la base de données
    data = pd.DataFrame({
        'lat': [], 
        'lon': [], 
        'date':[], 
        'time':[], 
        'path':[], 
        'orientation':[]
    })
    data = get_dataset(pictures_path, data)
    
    # On crée la carte
    m = folium.Map(location=[47, 1], tiles="OpenStreetMap", zoom_start=5)
    
    # On ajoute les emplacements    
    m = add_markers(m, data, env, width=300)

    # On enregistre au format html
    print("Enregistrement de la carte ...")
    m.save(env.result_path)
    
    # Info
    end = time.time()
    print(
        'Fin. Durée totale : ', int((end-start)//60), 
        'm', int((end-start)%60), 's'
    )