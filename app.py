from datetime import datetime
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask (__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Trabajador, RegistroHorario

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/entrada', methods=['GET', 'POST'])
def registroDeEntrada():
    if request.method == "POST":
        if not request.form['legajo'] or not request.form['dni4'] or not request.form['dependencia']:
            return render_template('error.html', error="Por favor, ingrese los datos requeridos.")
        if not request.form['legajo'].isdigit():
            return render_template ('error.html', error = "El legajo solo debe contener numeros.")
        else:
            legajoT = int(request.form['legajo'])
        trabajador_actual = Trabajador.query.filter_by(legajo = legajoT).first()
        if trabajador_actual is None:
            return render_template ('error.html', error = "El legajo ingresado no corresponde a ningun trabajador.")
        if not trabajador_actual.dni.endswith (request.form['dni4']):
            return render_template ('error.html', error = "Los ultimos digitos del DNI ingresado no corresponde a ningun trabajador.")
        dia = datetime.now().date()
        registroE = RegistroHorario.query.filter_by(idtrabajador = trabajador_actual.id, fecha = dia).first()
        if registroE:
            return render_template ('error.html', error = 'Ya se registro entrada.')
        else:
            registroEN = RegistroHorario(idtrabajador  = trabajador_actual.id, fecha = dia, horaentrada = datetime.now().time(), dependencia = request.form['dependencia'])
            db.session.add (registroEN)
            db.session.commit()
            print("Registro guardado en la base")
            return render_template('inicio.html', mensaje='Entrada registrada correctamente.')
    return render_template ('registrar_entrada.html')

@app.route('/salida', methods=['GET', 'POST'])
def registroDeSalida():
    if request.method == "POST":
        if not request.form['legajo'] or not request.form['dni4']:
            return render_template('error.html', error="Por favor, ingrese los datos requeridos.")
        if not request.form['legajo'].isdigit():
            return render_template('error.html', error="El legajo solo debe contener numeros.")
        else:
            legajoT = int(request.form['legajo'])
        trabajador_actual = Trabajador.query.filter_by(legajo=legajoT).first()
        if trabajador_actual is None:
            return render_template('error.html', error="El legajo ingresado no corresponde a ningun trabajador.")
        if not trabajador_actual.dni.endswith(request.form['dni4']):
            return render_template('error.html', error="Los ultimos digitos del DNI ingresado no corresponde a ningun trabajador.")
        dia = datetime.now().date()
        registroS = RegistroHorario.query.filter_by(idtrabajador=trabajador_actual.id, fecha=dia).first()
        if registroS is None:
            return render_template('error.html', error="No se ha registrado una entrada para hoy.")
        if registroS.horasalida is not None:
            return render_template('error.html', error="Ya se ha registrado la salida para hoy.")
        return render_template('confirmar_salida.html', legajo=trabajador_actual.legajo, fecha_entrada=registroS.fecha,hora_entrada=registroS.horaentrada,dependencia_entrada=registroS.dependencia)
    else:
        return render_template('registrar_salida.html')

@app.route('/confirmarDependencia', methods=['GET', 'POST'])
def confirmarSalida():
    if request.method == 'POST':
        if not request.form['dependencia']:
            return render_template('error.html', error="La dependencia ingresada no es valida.")
        else:
            legajoT = int(request.form.get('legajo'))
            dni4 = request.form.get('dni4')
            trabajador_actual = Trabajador.query.filter_by(legajo=legajoT).first()
            if trabajador_actual is not None and trabajador_actual.dni.endswith(dni4):
                dia = datetime.now().date()
                registroS = RegistroHorario.query.filter_by(idtrabajador=trabajador_actual.id, fecha=dia).first()
                if registroS is not None:
                    if request.form ['dependencia'] == registroS.dependencia:
                        registroS.horasalida = datetime.now().time()
                        db.session.commit()
                    else:
                        return render_template ('error.html', error = "La dependencia ingresada no corresponde a la entrada registrada.")
                    return render_template('inicio.html', mensaje="Registro de salida exitoso.")
                else:
                    return render_template('error.html', error="No se ha registrado entrada.")
    else:
        return render_template('confirmar_salida.html')


@app.route('/consultar', methods=['GET', 'POST'])
def consultarRegistro():
    if request.method == "POST":
        if not request.form['legajo'] or not request.form ['dni4'] or not request.form['fechainicio'] or not request.form['fechafin']:
            return render_template ('error.html', error = "Por favor, ingrese los datos requeridos.")
        else:
            if not request.form['legajo'].isdigit():
                return render_template('error.html', error = "El legajo solo debe contener numeros.")
            legajoT = int(request.form['legajo'])
            trabajador_actual = Trabajador.query.filter_by(legajo = legajoT).first()
            if trabajador_actual is None:
                return render_template ('error.html', error = "El legajo ingresado no es valido.")
            if not trabajador_actual.dni.endswith (request.form['dni4']):
                return render_template ('error.html', error = "El DNI ingresado no es valido")
            registroH = RegistroHorario.query.filter_by (idtrabajador = trabajador_actual.id, fecha = request.form['fechainicio']).first()
            if registroH is None:
                return render_template ('error.html', error = "La fecha de inicio ingresada no es valida")
            registroH = RegistroHorario.query.filter_by (idtrabajador = trabajador_actual.id, fecha = request.form['fechafin']).first()
            if registroH is None:
                return render_template ('error.html', error = "La fecha de fin ingresada no es valida")
            fecha_inicio = datetime.strptime(request.form['fechainicio'], '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(request.form['fechafin'], '%Y-%m-%d').date()
            consultarR = RegistroHorario.query.filter(RegistroHorario.idtrabajador == trabajador_actual.id,RegistroHorario.fecha >= fecha_inicio,RegistroHorario.fecha <= fecha_fin).order_by(RegistroHorario.fecha).all()
            return render_template('mostrar_registros.html',registros=consultarR,trabajador=trabajador_actual,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin)

    else:
        return render_template('consultar_registros.html')
    
    
@app.route ('/informe', methods = ['GET', 'POST'])
def generarInforme ():
    if request.method == "POST":
        if not request.form['legajo'] or not request.form['dni4']:
            return render_template ('error.html', error = "Los datos ingresados no son validos.")
        if not request.form['legajo'].isdigit():
            return render_template ('error.html', error = "El legajo solo debe contener numeros.")
        legajoT = int (request.form['legajo'])
        trabajador_actual = Trabajador.query.filter_by(legajo = legajoT, funcion = "AD").first()
        if trabajador_actual is None:
            return render_template ('error.html', error = "El legajo ingresado no es valido.")
        if not trabajador_actual.dni.endswith(request.form['dni4']):
            return render_template ('error.html', error = "El DNI ingresado no es valido.")
        return render_template('formulario_filtro.html', trabajador=trabajador_actual)
    else:
        return render_template ('generar_informe.html')


@app.route ('/ver_informe', methods = ['POST', 'GET'])
def verInforme():
    if request.method == "POST":
        if not request.form['fechainicio'] or not request.form['fechafin'] or not request.form['funcion'] or not request.form['dependencia']:
            return render_template ('error.html', error = "Los datos ingresados no son validos.")
        fechainicio = request.form['fechainicio']
        fechafin = request.form['fechafin']
        fechainicio = datetime.strptime(fechainicio, '%Y-%m-%d').date()
        fechafin = datetime.strptime(fechafin, '%Y-%m-%d').date()
        legajo = int(request.form['legajo'])
        trabajadorOb = Trabajador.query.filter_by(legajo=legajo).first()
        if not trabajadorOb:
            return render_template('error.html', error="Trabajador no encontrado.")
        registrosTotal = RegistroHorario.query.filter(RegistroHorario.fecha >= fechainicio,RegistroHorario.fecha <= fechafin)
        if request.form['dependencia'] != "todas":
            registrosTotal = registrosTotal.filter(RegistroHorario.dependencia == request.form['dependencia'])
        registros = registrosTotal.all()
        if request.form['funcion'] != "todas":
            registros = [regi for regi in registros if regi.trabajador is not None and regi.trabajador.funcion == request.form['funcion']]
        registros.sort(key=lambda regi: regi.trabajador.apellido if regi.trabajador else '')
        for registro in registros:
            if registro.horaentrada and registro.horasalida:
                hora_entrada = datetime.combine(registro.fecha, registro.horaentrada)
                hora_salida = datetime.combine(registro.fecha, registro.horasalida)
                diferencia = hora_salida - hora_entrada
                horas = diferencia.seconds // 3600
                minutos = (diferencia.seconds % 3600) // 60
                registro.horas_trabajadas = f"{horas}h {minutos}m"
            else:
                registro.horas_trabajadas = "0h 0m"
        registros.sort(key=lambda regi: regi.trabajador.apellido if regi.trabajador else '')
        return render_template('mostrar_informe.html', registros=registros, fecha_inicio=fechainicio, fecha_fin=fechafin, trabajador=trabajadorOb)
    else:
        return render_template('generar_informe.html')
  

if __name__ == '__main__':
  print("Base de datos usada:", app.config['SQLALCHEMY_DATABASE_URI'])
  with app.app_context():
      pass
    ##db.create_all()
  app.run(debug=True)