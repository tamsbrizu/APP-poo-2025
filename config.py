import os

SECRET_KEY = "POO2025"
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'basedatos.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
