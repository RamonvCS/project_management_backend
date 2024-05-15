from flask import jsonify, request
import mariadb
from flask import jsonify, request
import mariadb
import sys
from config import DATABASE_CONFIG

conn = mariadb.connect(**DATABASE_CONFIG)

#------------------------------------** FUNCION NEW PROJECT **----------------------------------------
# Abielmelex

def get_all_members():
    try:
        members_info = {}  # Diccionario para almacenar la información de los miembros y sus proyectos

        # Inicia un cursor de base de datos
        cursor = conn.cursor()
        
        # Obtiene todos los proyectos disponibles
        cursor.execute("SELECT project_id, project_name FROM projects")
        all_projects = cursor.fetchall()
        for project in all_projects:
            project_id, project_name = project
            # Inicializa la estructura de datos para cada proyecto
            members_info[project_id] = {"project_name": project_name, "members": []}

        # Obtiene la información de los miembros y los proyectos a los que pertenecen
        cursor.execute("""
                SELECT m.member_id, m.member_name, m.role, p.project_id, p.project_name
                FROM team_members m
                JOIN projects p ON m.project_id = p.project_id
            """)
        members = cursor.fetchall()
        
        # Organiza a los miembros por sus proyectos
        for member in members:
            member_info = {
                "member_id": member[0],  
                "member_name": member[1],  
                "role": member[2],
            }

            project_id = member[3]
            if project_id in members_info:
                members_info[project_id]["members"].append(member_info)

        # Prepara la respuesta
        response_data = [{
            "project_id": project_id, 
            "project_name": project_data["project_name"], 
            "members": project_data["members"]
        } for project_id, project_data in members_info.items()
        ]

        return jsonify({"members": response_data}), 200

    except Exception as e:
        # Maneja excepciones y devuelve un mensaje de error
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()  # Cierra el cursor de la base de datos

#------------------------------------** FUNCION DELETE MEMBER **----------------------------------------

def delete_member(member_id):
    try:
        cursor = conn.cursor()  # Inicia un cursor de la base de datos
        
        # Comprueba si el miembro existe
        cursor.execute("SELECT * FROM team_members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()

        if member is None:
            # Si el miembro no existe, devuelve un mensaje y el estado 404 Not Found
            return jsonify({"error": "Member does not exist."}), 404
        
        # Comprueba si el miembro está asociado con una tarea
        cursor.execute("SELECT * FROM tasks WHERE member_id = %s", (member_id,))
        tasks = cursor.fetchall()

        if tasks:
            # Si existen tareas para el miembro, devuelve un mensaje y el estado 400 Bad Request
            return jsonify({"error": "Cannot delete member as they are associated with a task."}), 400
        else:
            # Si no existen tareas para el miembro, elimina el miembro
            cursor.execute("DELETE FROM team_members WHERE member_id = %s", (member_id,))
            conn.commit()
            return jsonify({"message": "Member deleted successfully."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()  # Cierra el cursor de la base de datos

#------------------------------------** FUNCION UPDATE MEMBER **----------------------------------------

# Actualizar los datos del miembro en la base de datos
def update_member(project_id, member_id):
    datos = request.json  # Obtiene los datos del miembro desde la solicitud
    member_name = datos.get('member_name')
    role = datos.get('role')

    try:
        with conn.cursor() as cursor:
            # Verifica si el proyecto existe
            cursor.execute("SELECT project_id FROM projects WHERE project_id = ?", (project_id,))
            project = cursor.fetchone()
            if not project:
                return jsonify({"error": "Proyecto no encontrado"}), 404

            # Verifica si el miembro existe en el proyecto especificado
            cursor.execute("SELECT member_id FROM team_members WHERE member_id = ? AND project_id = ?", (member_id, project_id))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "Miembro no encontrado en el proyecto especificado"}), 404

            # Realiza la actualización de los datos del miembro
            cursor.execute("UPDATE team_members SET member_name = ?, role = ? WHERE member_id = ? AND project_id = ?", 
                           (member_name, role, member_id, project_id))
            if cursor.rowcount == 0:
                # Si no se actualizaron filas, indica que el miembro o el proyecto no existen
                return jsonify({"error": "No se actualizó ningún miembro, verifique los identificadores"}), 404
            conn.commit()
    except mariadb.Error as e:
        conn.rollback()
        print(f"Error updating member: {e}")
        return jsonify({"error": "Error al actualizar miembro", "details": str(e)}), 500

    return jsonify({"message": "Miembro actualizado correctamente"}), 200

#------------------------------------** FUNCION POST MEMBERS **----------------------------------------

# Insertar datos del nuevo miembro en la base de datos
def post_members(project_id):
    cursor = conn.cursor()  # Inicia un cursor de la base de datos
    
    datos = request.json  # Obtiene los datos del nuevo miembro desde la solicitud
    role = datos.get('role')
    member_name = datos.get('member_name')
  
    try:
        # Inserta los datos del nuevo miembro en la base de datos
        cursor.execute("INSERT INTO team_members (member_name, role, project_id) VALUES (?, ?, ?)", (member_name, role, project_id))
        conn.commit()
    except mariadb.Error as e:
        print(f"Error de base de datos: {e}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

    return jsonify({"message": "Miembro añadido correctamente", "role": role}), 201

#------------------------------------** FUNCION GET MEMBERS BY PROJECT **----------------------------------------

def get_members_by_project(project_id):
    try:
        with conn.cursor() as cursor:
            # Ejecuta la consulta SQL para obtener miembros que pertenecen a un proyecto específico
            cursor.execute("SELECT member_id, member_name FROM team_members WHERE project_id = ?", (project_id,))
            members = cursor.fetchall()
            # Prepara los datos para la respuesta
            member_data = [{'member_id': member[0], 'member_name': member[1]} for member in members]
            return jsonify(member_data)  # Retorna los datos de los miembros en formato JSON
    except mariadb.Error as e:
        # Maneja posibles errores de la consulta
        print(f"Database query error: {e}")
        return jsonify({"error": "Error retrieving members"}), 500  # Retorna un mensaje de error y estado 500
