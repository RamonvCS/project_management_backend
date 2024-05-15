# Importaciones
from flask import jsonify, request
import mariadb
import sys
from config import DATABASE_CONFIG

def get_db_connection():
    try:
        conn = mariadb.connect(**DATABASE_CONFIG)
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

# Crea una nueva tarea
def create_task(project_id, member_id):
    conn = get_db_connection()
    try:
        data = request.json
        task_name = data.get('task_name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task_name, start_date, end_date, member_id, project_id) VALUES (?, ?, ?, ?, ?)",
                       (task_name, start_date, end_date, member_id, project_id))
        conn.commit()
        return jsonify({"message": "New task created successfully"}), 201
    except mariadb.Error as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#------------------------------------** FUNCION DELETE TASK **----------------------------------------
# Elimina una tarea existente
def delete_task(task_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Verifica si la tarea existe
        cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = cursor.fetchone()

        if task is None:
            return jsonify({"error": "Task does not exist."}), 404
        
        # Elimina la tarea
        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
        conn.commit()
        
        return jsonify({"message": "Task deleted successfully."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#------------------------------------** FUNCION GET ALL TASKS **----------------------------------------
# Obtiene todas las tareas
def get_all_tasks():
    conn = get_db_connection()
    try:
        projects_with_tasks = {}

        # Inicializar la lista de proyectos con sus datos
        cursor = conn.cursor()
        cursor.execute("SELECT project_id, project_name FROM projects")
        all_projects = cursor.fetchall()
        for project in all_projects:
            project_id, project_name = project
            projects_with_tasks[project_id] = {"project_name": project_name, "tasks": []}

        # Llenar los proyectos con las tareas existentes, incluyendo el nombre del miembro
        cursor.execute("""
            SELECT t.task_id, t.task_name, t.start_date, t.end_date, t.project_id, t.member_id, m.member_name
            FROM tasks t
            JOIN team_members m ON t.member_id = m.member_id
        """)
        tasks = cursor.fetchall()
        for task in tasks:
            task_info = {
                "task_id": task[0],
                "task_name": task[1],
                "start_date": task[2],
                "end_date": task[3],
                "member_id": task[5],
                "member_name": task[6]  # Añadido el nombre del miembro
            }
            project_id = task[4]
            if project_id in projects_with_tasks:
                projects_with_tasks[project_id]["tasks"].append(task_info)

        # Construir la respuesta JSON
        response_data = [
            {
                "project_id": project_id,
                "project_name": project_data["project_name"],
                "tasks": project_data["tasks"]
            } for project_id, project_data in projects_with_tasks.items()
        ]
        return jsonify({"data": response_data}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#------------------------------------** FUNCION UPDATE TASK **----------------------------------------
# Actualiza una tarea existente
def update_task(task_id, member_id):
    conn = get_db_connection()
    try:
        data = request.json
        task_name = data.get('task_name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET task_name = %s, start_date = %s, end_date = %s, member_id = %s WHERE task_id = %s",
                       (task_name, start_date, end_date, member_id, task_id))
        conn.commit()

        return jsonify({"message": "Record updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
