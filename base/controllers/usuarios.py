from flask import Flask, Blueprint, render_template, request, redirect, session, flash, url_for,g
from flask import flash
from flask_bcrypt import Bcrypt
from datetime import datetime, date

from base.models.usuario import Usuario
from base.models.asesorias import Asesoria


import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

bcrypt = Bcrypt()

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@bp.route('/registrar', methods=['POST'])
def registrar():
    if not Usuario.validar_usuario(request.form):
        return redirect('/')
    
    pass_encrypt = bcrypt.generate_password_hash(request.form['password'])

    form ={
        'nombre': request.form['nombre'],
        'apellido': request.form['apellido'],
        'email': request.form['email'],
        'password': pass_encrypt
    }

    nuevo_id = Usuario.guardar(form)
    session['usuario_id'] = nuevo_id

    return redirect(url_for('usuarios.dashboard'))

@bp.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect('/')
    
    form ={"id":session['usuario_id']}
    usuario = Usuario.obtener_por_id(form)

    asesorias = Asesoria.obtener_todo()

    future_date = datetime.now().date()

    # Asegúrate de que las fechas de las asesorías estén en formato date
    asesoria_fechas = [asesoria.fecha for asesoria in asesorias if asesoria.fecha]  # Lista de fechas

    return render_template('dashboard.html', usuario=usuario, asesorias=asesorias, future_date=future_date, asesoria_fechas=asesoria_fechas)



@bp.route('/login', methods=['GET','POST'])
def login():
    form_data = request.form
    usuario = Usuario.obtener_por_email(form_data)

    if not usuario:
        flash('Usuario o contraseña incorrecta', "login")
        return redirect('/')
    
    if not bcrypt.check_password_hash(usuario.password, form_data['password']):
        flash('Contraseña incorrecta', "login")
        return redirect('/')
    
    session['usuario_id'] = usuario.id
    return redirect(url_for('usuarios.dashboard'))

@bp.before_app_request
def load_logged_in_user():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        g.user = None
    else:
        # Obtener usuario por ID y almacenarlo en `g.user`
        g.user = Usuario.obtener_por_id(usuario_id)


import functools

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('usuarios.login'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')