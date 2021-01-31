# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 19:45:14 2021

@author: Alexandre Banon
"""

import os
import copy
import pandas as pd

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS



def get_exif(filename):
    """Extrait les informations numériques EXIF d'une image. Les données brutes
    sont aussi décryptée.

    Parameters
    ----------
    filename : str
        Nom du fichier à partir duquel charger l'image.

    Returns
    -------
    exif : dict
        Données EXIF partiellement décryptées.
    """
    
    # Ouverture du fichier image
    exif = Image.open(filename)._getexif()
    
    if exif is not None:
        for key, value in copy.deepcopy(exif).items():
            name = TAGS.get(key, key)
            exif[name] = exif.pop(key)
        
        if 'GPSInfo' in exif:
            for key in copy.deepcopy(exif['GPSInfo']).keys():
                name = GPSTAGS.get(key,key)
                exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)
        else:
            print("Pas d'information de géolocalisation dans cette image.")
        
    return exif



def get_coordinates(info):
    """Extrait et décrypte les coordonnées géographiques.

    Parameters
    ----------
    info : dict
        Partie `'GPSInfo'` des données EXIF décryptées.

    Returns
    -------
    results : list
        Renvoie la liste de Latitude/Longitude si ces données existent.
    """
    
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info[key] = ( 
                str(e[0]) + '°' +
                str(e[1]) + '′' +
                str(e[2]) + '″ ' +
                ref 
            )
    
    if 'Latitude' in info and 'Longitude' in info:
        results = [info['Latitude'], info['Longitude']]
        return results



def get_decimal_coordinates(info):
    """Extrait et décrypte les coordonnées géographiques sous format décimal.

    Parameters
    ----------
    info : dict
        Partie `'GPSInfo'` des données EXIF décryptées.

    Returns
    -------
    results : list
        Renvoie la liste de Latitude/Longitude si ces données existent.
    """
    
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info[key] = (
                e[0] +
                e[1] / 60. +
                e[2] / 3600.
            ) 
            info[key] *= -1 if ref in ['S','W'] else 1
        
    if 'Latitude' in info and 'Longitude' in info:
        results = [info['Latitude'], info['Longitude']]
        return results



def get_dataset(folder, data, main_call=True):
    """Met à jour le DataFrame d'entrée '`data'` en y ajoutant les données de 
    localisation des images trouvées dans dans le dossier `'folder'`. L'appel
    de cette fonction est récurcive, afin d'extraire toutes les images si l'on
    renseigne un dossier.
    
    Parameters
    ----------
    folder : str
        Dossier ou fichier dans lequel extraire des information de 
        photographie.
        
    data : DataFrame
        Données contenant les informations de chaque photo à ajouter.
        
    main_call : bool, defautl=True
        Décris si l'appel de la fonction est la première, ou issue d'un appel
        récurcif.
        
    Returns
    -------
    data : DataFrame
        Données contenant les informations de chaque photo à ajouter.
    """
    
    if main_call:
        print("Récupération des données de géolocalisation ...")
    
    coords = []
    dates  = []
    times  = []
    paths  = []
    oriens = []
    
    for el_path in os.listdir(folder):
        
        el_path = os.path.join(folder, el_path)
        
        # Si c'est un fichier, on regarde s'il est sous un format d'image et on
        # enregistre les informations
        if os.path.isfile(el_path) and \
            el_path.split('.')[1] in ['png', 'jpg', 'jpeg', 'JPG']:
            
            exif = get_exif(el_path)
            
            if exif is not None and 'GPSInfo' in exif.keys():
                
                datetime = exif['DateTime'].split(' ')
                coord  = get_decimal_coordinates(exif['GPSInfo'])

                if coord is not None:
                    
                    coords += [coord]
                    dates  += [datetime[0]]
                    times  += [datetime[1]]
                    paths  += [el_path]
                    oriens += [exif['Orientation']]
            
        # Si c'est un dossier, on cherche dedans de manière récursive
        elif os.path.isdir(el_path):
            
            sub_data = get_dataset(el_path, data, main_call=False)
            data     = data.append(sub_data)
            data     = data.drop_duplicates(ignore_index=True)
            
    # On sauvegarde les résultat dans un même DataFrame
    tmp_data = pd.DataFrame({
        'lat':         [coord[0] for coord in coords],
        'lon':         [coord[1] for coord in coords],
        'date':        [date for date in dates],
        'time':        [time for time in times],
        'path':        [el_path for el_path in paths],
        'orientation': [orien for orien in oriens]
    })
    
    data = data.append(tmp_data)
    data = data.drop_duplicates(ignore_index=True)
    
    return data