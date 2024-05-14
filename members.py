from flask import jsonify, request
import mariadb
from flask import jsonify, request
import mariadb
import sys
from config import DATABASE_CONFIG

conn = mariadb.connect(**DATABASE_CONFIG)

##Abielmelex
def get_all_members():
    try:
        members_info = {}

        # Start a database cursor
        cursor = conn.cursor()
        
            # Fetch members and the projects they belong to
        cursor.execute("SELECT project_id, project_name FROM projects")
        all_projects = cursor.fetchall()
        for project in all_projects:
            project_id, project_name = project
            members_info[project_id] = {"project_name": project_name, "members": []}

        # Llenar los proyectos con las tareas existentes, incluyendo el nombre del miembro
        cursor.execute("""
                SELECT m.member_id, m.member_name, m.role, p.project_id, p.project_name
                FROM team_members m
                JOIN projects p ON m.project_id = p.project_id
            """)
        members = cursor.fetchall()
        
        # Organize members by their projects
        for member in members:
            member_info = {
                "member_id": member[0],  # Ensures member ID is included
                "member_name": member[1],  # Ensures member name is included
                "role": member[2],
            }

            project_id = member[3]
            project_name = member[4]
            if project_id in members_info:
                members_info[project_id]["members"].append(member_info)

        # Prepare the response
        response_data = [{
            "project_id": project_id, 
            "project_name": project_data["project_name"], 
            "members": project_data["members"]
        } for project_id, project_data in members_info.items()
        ]

        return jsonify({"members": response_data}), 200

    except Exception as e:
        # Handle exceptions and return an error message
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

def delete_member(member_id):
    try:
        cursor = conn.cursor()
        
        # Check if member exists
        cursor.execute("SELECT * FROM team_members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()

        if member is None:
            # If member does not exist, return a message and 404 Not Found status
            return jsonify({"error": "Member does not exist."}), 404
        
        # Check if member is associated with a task
        cursor.execute("SELECT * FROM tasks WHERE member_id = %s", (member_id,))
        tasks = cursor.fetchall()

        if tasks:
            # If tasks exist for the member, return a message and 400 Bad Request status
            return jsonify({"error": "Cannot delete member as they are associated with a task."}), 400
        else:
            # If no tasks exist for the member, delete the member
            cursor.execute("DELETE FROM team_members WHERE member_id = %s", (member_id,))
            conn.commit()
            return jsonify({"message": "Member deleted successfully."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# actualizar los dato del miembro en la base de datos
def update_member(project_id, member_id):
    datos = request.json
    member_name = datos.get('member_name')
    role = datos.get('role')

    try:
        with conn.cursor() as cursor:
            # Verifica si el proyecto existe
            cursor.execute("SELECT project_id FROM projects WHERE project_id = ?", (project_id,))
            project = cursor.fetchone()
            if not project:
                return jsonify({"error": "Proyecto no encontrado"}), 404

            # Verifica si el miembro existe
            cursor.execute("SELECT member_id FROM team_members WHERE member_id = ? AND project_id = ?", (member_id, project_id))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "Miembro no encontrado en el proyecto especificado"}), 404

            # Realiza la actualización
            cursor.execute("UPDATE team_members SET member_name = ?, role = ? WHERE member_id = ? AND project_id = ?", 
                           (member_name, role, member_id, project_id))
            if cursor.rowcount == 0:
                # No se actualizaron filas, lo que indica que el miembro o el proyecto no existen
                return jsonify({"error": "No se actualizó ningún miembro, verifique los identificadores"}), 404
            conn.commit()
    except mariadb.Error as e:
        conn.rollback()
        print(f"Error updating member: {e}")
        return jsonify({"error": "Error al actualizar miembro", "details": str(e)}), 500

    return jsonify({"message": "Miembro actualizado correctamente"}), 200


        
#insertar datos del nuevo miembro en la base de datos
def post_members(project_id):
    cursor = conn.cursor()
    
    datos = request.json
    role = datos.get('role')
    member_name = datos.get('member_name')
  
    try:
        cursor.execute("INSERT INTO team_members ( member_name, role, project_id) VALUES ( ?, ?, ?)", ( member_name, role, project_id))
        conn.commit()
    except mariadb.Error as e:
        print(f"Error de base de datos: {e}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

    return jsonify({"message": "Miembro añadido correctamente", "role": role}), 201



def get_members_by_project(project_id):
    try:
        with conn.cursor() as cursor:
            # Ejecuta la consulta SQL para obtener miembros que pertenecen a un proyecto específico
            cursor.execute("SELECT member_id, member_name FROM team_members WHERE project_id = ?", (project_id,))
            members = cursor.fetchall()
            # Prepara los datos para la respuesta
            member_data = [{'member_id': member[0], 'member_name': member[1]} for member in members]
            return jsonify(member_data)
    except mariadb.Error as e:
        # Maneja posibles errores de la consulta
        print(f"Database query error: {e}")
        return jsonify({"error": "Error retrieving members"}), 500

