from flask import jsonify, request
import mariadb
import sys
from config import DATABASE_CONFIG

conn = mariadb.connect(**DATABASE_CONFIG)

def create_task(project_id, member_id):
    data = request.json
    task_name = data.get('task_name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    try:
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

def delete_task(task_id):
    try:
        cursor = conn.cursor()
        
        # Check if task exists
        cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = cursor.fetchone()

        if task is None:
            # If task does not exist, return a message and 404 Not Found status
            return jsonify({"error": "Task does not exist."}), 404
        
        # Delete the task
        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
        conn.commit()
        
        return jsonify({"message": "Task deleted successfully."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

def get_all_tasks():
    try:
        tasks_by_project = {}

        # Obtener todas las tareas junto con la información del proyecto
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.task_id, t.task_name, t.start_date, t.end_date, t.project_id, p.project_name 
                FROM tasks t 
                JOIN projects p ON t.project_id = p.project_id
            """)
            tasks = cursor.fetchall()
            for task in tasks:
                task_info = {
                    "task_id": task[0],
                    "task_name": task[1],
                    "start_date": task[2],
                    "end_date": task[3]
                }
                project_id = task[4]
                project_name = task[5]
                if project_id not in tasks_by_project:
                    tasks_by_project[project_id] = {"project_name": project_name, "tasks": []}
                tasks_by_project[project_id]["tasks"].append(task_info)

        # Construir la respuesta JSON
        response_data = [{"project_id": project_id, "project_name": project_data["project_name"], "tasks": project_data["tasks"]} for project_id, project_data in tasks_by_project.items()]
        return jsonify({"data": response_data}), 200
    except mariadb.Error as e:
        return jsonify({"error": "An error occurred while fetching tasks"}), 500

def update_task(task_id):
    try:
        data = request.json
        task_name = data.get('task_name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET task_name = %s, start_date = %s, end_date = %s WHERE task_id = %s",
                       (task_name, start_date, end_date, task_id))
        conn.commit()

        return jsonify({"message": "Record updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
