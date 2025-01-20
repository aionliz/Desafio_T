from base.config.mysqlconnection import connectToMySQL

from flask import flash

import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Usuario:
    def __init__(self, data):
        self.id = data['id']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def guardar(cls, form):
        query = "INSERT INTO usuarios (nombre, apellido, email, password, created_at, updated_at) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s, NOW(), NOW());"
        result = connectToMySQL('esquema_t').query_db(query, form)
        return result
    
    @staticmethod
    def validar_usuario(form):
        is_valid = True

        if len(form['nombre']) < 3:
            flash('El nombre debe tener al menos 3 caracteres', "register")
            is_valid = False
        
        if len(form['apellido']) < 3:
            flash('El apellido debe tener al menos 3 caracteres', "register")
            is_valid = False

        if not EMAIL_REGEX.match(form['email']):
            flash('Correo inválido', "register")
            is_valid = False

        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        results = connectToMySQL('esquema_t').query_db(query, form)
        if len(results) >= 1:
            flash('Correo ya registrado')
            is_valid = False

        if len(form['password']) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', "register")
            is_valid = False

        if form['password'] != form['confirm']:
            flash('Las contraseñas no coinciden', "register")
            is_valid = False

        return is_valid
    
    # Método para obtener un usuario por su correo electrónico
    @classmethod
    def obtener_por_email(cls, form):
        # Consulta para obtener el usuario por correo
        query = "SELECT * FROM usuarios WHERE email = %(email)s"
        results = connectToMySQL('esquema_t').query_db(query, form)
        
        # Si el usuario existe, devolvemos la instancia del usuario
        if len(results) == 1:
            usuario = cls(results[0])
            return usuario
        else:
            return False

    # Método para obtener un usuario por su ID
    @classmethod
    def obtener_por_id(cls, id):
        # Consulta para obtener el usuario por ID
        query = "SELECT * FROM usuarios WHERE id = %(id)s"
        data = {'id' : id}
        results = connectToMySQL('esquema_t').query_db(query, data)
        
        if results :
            return cls(results[0])
        return None

    @classmethod
    def obtener_todos_excepto_actual(cls, data):
        query = "SELECT * FROM usuarios WHERE id != %(id)s;"
        results = connectToMySQL('esquema_t').query_db(query, data)
        usuarios = []
        for usuario in results:
            usuarios.append(cls(usuario))
        return usuarios
    
    @classmethod
    def obtener_todos(cls):
        query = "SELECT * FROM usuarios;"
        results = connectToMySQL('esquema_t').query_db(query)
        usuarios = []
        for row in results:
            usuarios.append(cls(row))
        return usuarios
    
    # Método para actualizar los datos de un usuario
    @classmethod
    def actualizar(cls, formulario):
        # Actualizamos los datos del usuario con el ID especificado
        query = "UPDATE usuarios SET nombre = %(nombre)s, apellido=%(apellido)s, email=%(email)s WHERE id=%(id)s"
        result = connectToMySQL('usuarios').query_db(query, formulario)
        return result
    
    @classmethod
    def borrar(cls, diccionario):
        query = "DELETE FROM usuarios WHERE id = %(id)s"
        result = connectToMySQL('usuarios').query_db(query, diccionario)
        return result

