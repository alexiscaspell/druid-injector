# druid-injector

> Proyecto base para aplicaciones REST con python


![alt text](img/python.png)

## REQUERIMIENTOS

* **Python 3.7**
* **Docker**

## EJECUCION

### PYTHON

* Crear un virtualenv normalmente para python
* Con el virtualenv activado ejecutar `python app.py`

### DOCKER

* Pararse en la ruta raiz del proyecto con docker instalado y funcionando
* Pararse `./scripts/build.sh`
* Ejecutar `docker run -it -p 5000:5000 druid-injector:latest`

## PAGINAS

[Docker python 3.7 apine](https://hub.docker.com/_/python)
