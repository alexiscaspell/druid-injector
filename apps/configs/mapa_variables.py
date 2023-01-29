from logging import INFO, ERROR, WARNING, DEBUG
import sys
import os

def is_environment_param():
    return len(sys.argv)>1 and str(sys.argv) in ["development","production"]

APP_NAME="DRUID_INJECTOR"
ENVIRONMENT_MODE = str(str(sys.argv[1]) if is_environment_param() else os.environ.get(f"{APP_NAME}".upper()+"_ENVIRONMENT_MODE", "development")).upper()

NO_MOSTRAR = ["DEBUG_MODE","LOG_LEVELS","DIRECTORIO_LOGS"]

DEVELOPMENT = {
    "DEBUG_MODE": True,
    "PYTHON_HOST": "0.0.0.0",
    "PYTHON_PORT":  5000,
    "API_BASE_PATH": "/api",
    "LOG_LEVELS": [INFO, ERROR, WARNING, DEBUG],
    "DIRECTORIO_LOGS": "./logs",
    "ENV": ENVIRONMENT_MODE,
    "DRUID_HOST": "localhost",
    "DRUID_PORT": 8090,
    "REDIS_HOST":"localhost",
    "REDIS_PORT":6379,
    "REDIS_PASSWD":None
}
PRODUCTION = {
    "DEBUG_MODE": False,
    "PYTHON_HOST": "0.0.0.0",
    "PYTHON_PORT":  5000,
    "API_BASE_PATH": "/api",
    "LOG_LEVELS":  [INFO, ERROR],
    "DIRECTORIO_LOGS": "./logs",
    "ENV": ENVIRONMENT_MODE
}

