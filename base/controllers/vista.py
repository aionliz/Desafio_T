from flask import Blueprint, render_template, redirect, request, session, flash, url_for, g 
from datetime import datetime, date


from base.models.asesorias import Asesoria
from base.models.usuario import Usuario

bp = Blueprint('vista', __name__, url_prefix='/vista')

from base.controllers.usuarios import login_required

@bp.route('/view')
def view():
    return render_template('auth.html')

@bp.route('/new', methods=['GET'])
@login_required
def new():
    
    form = {"id": g.user.id}
    usuario = Usuario.obtener_por_id(form)
    usuarios = Usuario.obtener_todos_excepto_actual(form)
    future_date = datetime.now().date() 
    return render_template('create.html', usuario=usuario, usuarios=usuarios, future_date=future_date)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    fecha_str = request.form['fecha']
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Fecha no válida", "danger")
        return redirect(url_for('vista.new'))

    if fecha < date.today():
        flash("No puedes elegir una fecha pasada.", "danger")
        return redirect(url_for('vista.new'))

    form_data = request.form.to_dict()
    form_data['fecha'] = fecha
    
    if not Asesoria.validar_asesoria(request.form):
        flash("Hubo un error con la validación de la asesoría.", "debug")
        return redirect(url_for('vista.new')) 
    

    Asesoria.guardar(request.form)
    flash('Asesoría creada exitosamente', 'success')
    return redirect(url_for('usuarios.dashboard'))

@bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit(id):
    form = {"id": g.user.id}
    usuario = Usuario.obtener_por_id(form)

    data_asesoria = {"id": id}
    asesoria = Asesoria.get_by_id(data_asesoria)

    if not asesoria:
        flash("Asesoría no encontrada.", "danger")
        return redirect(url_for('usuarios.dashboard'))

    if asesoria.usuario_id != g.user.id:
        return redirect(url_for('usuarios.dashboard'))    
    
    usuarios = Usuario.obtener_todos()
    tutor_actual = Usuario.obtener_por_id({"id": asesoria.tutor_id}) if asesoria.tutor_id else None
    puede_cambiar_tutor = True

    today = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        fecha_str = request.form['fecha']
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Fecha no válida", "danger")
            return redirect(url_for('vista.edit', id=id))

        if fecha < date.today():
            flash("No puedes elegir una fecha pasada.", "danger")
            return redirect(url_for('vista.edit', id=id))

        # Formulario con los datos actualizados
        form_data = {
            "id": id,
            "tema": request.form['tema'],
            "fecha": fecha,
            "duracion": request.form['duracion'],
            "nota": request.form['nota'],
            "tutor_id": request.form['tutor_id']
        }

        # Validar los datos del formulario
        if not Asesoria.validar_asesoria(request.form):
            flash("Hubo un error en la validación de los datos.", "danger")
            return redirect(url_for('vista.edit', id=id)) 

        # Llamar al método de actualización con los datos del formulario
        Asesoria.update_asesoria(form_data)
        # Redirigir al dashboard después de actualizar
        flash('Asesoría actualizada con éxito', 'success')
        return redirect(url_for('usuarios.dashboard', id=g.user.id))


    return render_template('editar.html', 
                            usuario=usuario, 
                            asesoria=asesoria, 
                            usuarios=usuarios, 
                            tutor_actual=tutor_actual, 
                            puede_cambiar_tutor=puede_cambiar_tutor,
                            today=today)

@bp.route('/ver/<int:id>', methods=['GET'])
@login_required
def ver(id):
    # Utilizamos g.user para acceder al usuario logueado
    usuario = g.user  # Aquí obtenemos el usuario logueado directamente
    data_asesoria = {"id": id}
    asesoria = Asesoria.obtener_por_id_con_tutor(data_asesoria)

    # Verificamos si el usuario logueado es el solicitante
    puede_cambiar_tutor = asesoria.usuario_id == g.user.id
    usuarios = Usuario.obtener_todos_excepto_actual({"id": g.user.id})
    tutor_actual = Usuario.obtener_por_id({"id": asesoria.tutor_id}) if asesoria.tutor_id else None

    # Pasamos la información a la plantilla
    return render_template('ver.html', 
                            usuario=usuario, 
                            asesoria=asesoria, 
                            puede_cambiar_tutor=puede_cambiar_tutor, 
                            usuarios=usuarios, tutor_actual=tutor_actual)

@bp.route('/update_tutor_ver/<int:id>', methods=['POST'])
def update_tutor_ver(id):
    return actualizar_tutor(id, 'ver')

@bp.route('/update_tutor_editar/<int:id>', methods=['POST'])
def update_tutor_editar(id):
    return actualizar_tutor(id, 'editar')
def actualizar_tutor(id, pagina):
    if not g.user:
        return redirect('/logout')

    nuevo_tutor_id = request.form['tutor_id']
    data = {
        "id": id,
        "tutor_id": nuevo_tutor_id
    }
    Asesoria.update_tutor(data)  # Verifica que este método realmente actualice el tutor

    # Redirección según la página solicitada
    if pagina == 'ver':
        return redirect(url_for('vista.ver', id=id))
    elif pagina == 'editar':
        return redirect(url_for('usuarios.dashboard', id=g.user.id))

@bp.route('/update', methods=['POST'])
@login_required
def update():
    nueva_asesoria_id = request.form['id']
    fecha_str = request.form['fecha']
    
    # Convertir la fecha a formato de fecha (sin hora)
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Fecha no válida", "danger")
        return redirect(url_for('vista.edit', id=nueva_asesoria_id)) 
    
    # Validar que la fecha no sea pasada
    if fecha < date.today():
        flash("No puedes elegir una fecha pasada.", "danger")
        return redirect(url_for('vista.edit', id=nueva_asesoria_id))
    
    form = {
        "id": nueva_asesoria_id,
        "tema": request.form['tema'],
        "fecha": fecha.strftime('%Y-%m-%d'),
        "duracion": request.form['duracion'],
        "nota": request.form['nota'],
        "tutor_id": request.form['tutor_id']
    }
    
    # Validar los datos del formulario
    if not Asesoria.validar_asesoria(request.form):
        flash("Hubo un error en la validación de los datos.", "danger")
        return redirect(url_for('vista.edit', id=nueva_asesoria_id)) 
    
    # Llamar al método de actualización con los datos del formulario
    Asesoria.update_asesoria(form)

        # Redirigir al dashboard después de actualizar
    flash('Asesoría actualizada con éxito', 'success')
    # Redirigir al dashboard después de actualizar
    return redirect(url_for('usuarios.dashboard', id=g.user.id))
    
@bp.route('/borrar/<int:id>')
@login_required
def borrar(id):

    # Eliminar la asesoría
    data_asesoria = {"id": id}
    Asesoria.borrar(data_asesoria)

    # Redirigir al dashboard después de eliminar
    return redirect(url_for('usuarios.dashboard'))

