from base.config.mysqlconnection import connectToMySQL
from datetime import date


from flask import flash

class Asesoria:

    def __init__(self, data):
        self.id = data['id']
        self.tema = data['tema']
        self.fecha = data['fecha']
        self.duracion = data['duracion']
        self.nota = data['nota']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.usuario_id = data['usuario_id']
        self.tutor_id = data ['tutor_id']
        self.nombre_usuario = data['nombre_usuario']
        self.nombre_tutor = data.get('nombre_tutor')  # Aquí se asigna 'nombre_tutor'


    @classmethod
    def guardar(cls, form):
        print("Formulario recibido para guardar:", form)
        query = "INSERT INTO asesorias (tema, fecha, duracion, nota, usuario_id, tutor_id, created_at, updated_at) VALUES (%(tema)s, %(fecha)s, %(duracion)s, %(nota)s, %(usuario_id)s, %(tutor_id)s, NOW(), NOW());"
        result = connectToMySQL('esquema_t').query_db(query, form)
        return result
    
    @staticmethod
    def validar_asesoria(form):
        print(form) 
        is_valid = True
        # Validar tema
        if len(form['tema']) < 3:
            flash('El tema debe tener al menos 3 caracteres.', "validar_asesoria")
            is_valid = False
        # Validar fecha
        if not form['fecha']:
            flash('Debe ingresar una fecha.', "validar_asesoria")
            is_valid = False
        else:
            # Asegurarse de que la fecha no esté en el pasado
            try:
                fecha = form['fecha']  # Asumimos que la fecha viene en formato "YYYY-MM-DD"
                fecha_parts = fecha.split('-')  # Separamos la fecha en año, mes y día
                fecha_date = date(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2]))
                if fecha_date < date.today():
                    flash('La fecha no puede ser en el pasado.', "validar_asesoria")
                    is_valid = False
            except ValueError:
                flash('El formato de la fecha es incorrecto. Use el formato YYYY-MM-DD.', "validar_asesoria")
                is_valid = False


        # Validar duración
        if not form['duracion']:
            flash('Debe ingresar una duración.', "validar_asesoria")
            is_valid = False
        else:
            try:
                duracion = int(form['duracion'])
                if duracion <= 0 or duracion > 8:
                    flash('La duración debe ser un número positivo no mayor a 8.', "validar_asesoria")
                    is_valid = False
            except ValueError:
                flash('La duración debe ser un número válido.', "validar_asesoria")
                is_valid = False
        # Validar tutor_id
        if 'tutor_id' not in form or not form['tutor_id']:
            flash('Debe seleccionar un tutor.', "validar_asesoria")
            is_valid = False
        return is_valid

    
    @classmethod
    def obtener_todo(cls):
        query = "SELECT asesorias.* , usuarios.nombre as nombre_usuario FROM asesorias JOIN usuarios ON asesorias.usuario_id = usuarios.id"
        results = connectToMySQL('esquema_t').query_db(query)
        asesorias = []
        for asesoria in results:
            asesorias.append(cls(asesoria))
        return asesorias
    
    @classmethod
    def get_by_id(cls, data):
        query = "SELECT asesorias.* , usuarios.nombre as nombre_usuario FROM asesorias JOIN usuarios ON asesorias.usuario_id = usuarios.id WHERE asesorias.id = %(id)s"
        result = connectToMySQL('esquema_t').query_db(query, data)
        if result and len(result)> 0:
            return cls(result[0])
        return None
    
    @classmethod
    def update_asesoria(cls, form):
        # Si es necesario, convierte la fecha a un objeto 'date' sin la hora
        if 'fecha' in form and form['fecha']:
            fecha_parts = form['fecha'].split('-')  # Convertir la fecha en partes
            form['fecha'] = date(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2]))  # Aseguramos que solo la fecha sea guardada
        
        query = """
        UPDATE asesorias 
        SET tema = %(tema)s, 
            fecha = %(fecha)s, 
            duracion = %(duracion)s, 
            nota = %(nota)s, 
            tutor_id = %(tutor_id)s 
        WHERE id = %(id)s
        """
        result = connectToMySQL('esquema_t').query_db(query, form)
        return result
    
    @classmethod
    def borrar(cls, data):
        query = "DELETE FROM asesorias WHERE id = %(id)s"
        result = connectToMySQL('esquema_t').query_db(query, data)
        return result

    @classmethod
    def update_tutor(cls, data):
        query = "UPDATE asesorias SET tutor_id = %(tutor_id)s WHERE id = %(id)s"
        result = connectToMySQL('esquema_t').query_db(query, data)
        return result


    @classmethod
    def obtener_por_id_con_tutor(cls, data):
        query = """
            SELECT asesorias.*, usuarios.nombre AS nombre_usuario, tutores.nombre AS nombre_tutor 
            FROM asesorias 
            JOIN usuarios ON asesorias.usuario_id = usuarios.id 
            LEFT JOIN usuarios AS tutores ON asesorias.tutor_id = tutores.id 
            WHERE asesorias.id = %(id)s
        """
        result = connectToMySQL('esquema_t').query_db(query, data)
        if result:
            # Asegúrate de que el campo 'nombre_tutor' esté presente
            return cls(result[0])  # Esto asigna los valores de la consulta a la clase Asesoria
        return None


