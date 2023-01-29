import imp
import os
import re

from flask import Flask


def _nombre_archivo(ruta: str, extension=''):
    '''
    Devuelve el nombre del archivo al final de la ruta sin la extension
    '''
    return re.split('/', ruta)[-1].replace(extension, '')


def _es_directorio(ruta: str):
    '''
    Devuelve si la ruta no termina con .py
    '''
    return not ruta.endswith('.py')


def _cargar_rutas_de_archivos(ruta_base: str):
    '''
    Obtiene las rutas de todos los archivos .py dentro del directorio parametro, 
    es recursivo por lo que si hay carpetas dentro tambien busca ahi
    '''
    if not ruta_base.endswith('/'):
        ruta_base += '/'

    sub_rutas = os.listdir(ruta_base)
    if '__pycache__' in sub_rutas:
        sub_rutas.remove('__pycache__')

    rutas_archivos = [
        f'{ruta_base}{a}' for a in sub_rutas if not _es_directorio(a)
    ]

    directorios = [f'{ruta_base}{d}' for d in sub_rutas if _es_directorio(d)]

    for d in directorios:
        rutas_archivos.extend(_cargar_rutas_de_archivos(d))

    return rutas_archivos


def registrar_blue_prints(app: Flask, directorio_rutas: str):
    '''
    Registra todos los archivos .py del directorio como rutas para Flask,
    para esto los modulos deben tener estos 2 atributos:

    from flask import Blueprint\n
    blue_print = Blueprint('tu_nombre_de_ruta', __name__, url_prefix='/ejemplos')\n
    '''
    rutas = _cargar_rutas_de_archivos(directorio_rutas)

    for ruta_archivo in rutas:

        nombre_archivo = _nombre_archivo(ruta_archivo, '.py')
        modulo = imp.load_source(nombre_archivo, ruta_archivo)

        app.register_blueprint(modulo.blue_print)
