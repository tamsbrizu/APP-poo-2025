from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)

class Trabajador(db.Model):
    __tablename__ = "trabajador"
    id = db.Column(db.Integer, primary_key=True)
    apellido = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    legajo = db.Column(db.Integer, nullable=False, unique=True)
    horas = db.Column(db.Integer, nullable=False)
    funcion = db.Column(db.String(100), nullable=False)  # DO, AD, TE
    registrohorario = db.relationship('RegistroHorario', backref='trabajador')


class RegistroHorario(db.Model):
    __tablename__ = 'registrohorario'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date)
    horaentrada = db.Column(db.Time)
    horasalida = db.Column(db.Time)
    dependencia = db.Column(db.String(100), nullable=False)  # D01, D02, D03
    idtrabajador= db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)

