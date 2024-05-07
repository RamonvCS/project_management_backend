from flask import Flask, jsonify, request
import mariadb
import sys
from config import DATABASE_CONFIG

app = Flask(__name__)

try:
    conn = mariadb.connect(**DATABASE_CONFIG)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

# Ruta para obtener todos los proyectos
@app.route('/api/projects', methods=['GET'])
def projects():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT project_name, description, project_id, status FROM projects")
        rows = cursor.fetchall()
        projects = [
            {'project_name': row[0], 'description': row[1], 'project_id': row[2], 'status': row[3]} 
            for row in rows
        ]
        response = jsonify({'projects': projects})
        response.headers.add("Access-Control-Allow-Origin", '*')
        return response
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# Ruta 2: Create a new project in the database
@app.route('/api/new_project', methods=['POST'])
def new_project():
    data = request.json
    project_name = data.get('project_name')
    description = data.get('description')
    status = data.get('status')

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO projects (project_name, description, status) VALUES (?, ?, ?)", (project_name, description, status))
        conn.commit()
        return jsonify({"message": "Project inserted successfully"}), 201
    except mariadb.Error as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()

# Ruta 3: Create a new task for a specific member
@app.route('/api/new_task/<int:project_id>/<int:member_id>', methods=['POST'])
def new_task(project_id, member_id):
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

#ruta 4 Delete_member
@app.route('/api/delete_member/<int:member_id>', methods=['DELETE'])
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


#ruta 6 GET ALL TASK
@app.route('/api/get_all_tasks', methods=['GET'])
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
        response = jsonify({"data": response_data})
        response.headers.add("Content-Type", 'application/json')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except mariadb.Error as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred while fetching tasks"}), 500


#ruta 7 DELETE PROJECT
@app.route('/api/delete_project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        cursor = conn.cursor()
        
        # Check if project exists
        cursor.execute("SELECT * FROM projects WHERE project_id = %s", (project_id,))
        project = cursor.fetchone()

        if project is None:
            # If project does not exist, return a message and 404 Not Found status
            return jsonify({"error": "Project does not exist."}), 404
        
        # Check if project is associated with any tasks
        cursor.execute("SELECT * FROM tasks WHERE project_id = %s", (project_id,))
        tasks = cursor.fetchall()

        if tasks:
            # If tasks exist for the project, return a message and 400 Bad Request status
            return jsonify({"error": "Cannot delete project as it is associated with tasks."}), 400
        else:
            # If no tasks exist for the project, delete the project
            cursor.execute("DELETE FROM projects WHERE project_id = %s", (project_id,))
            conn.commit()
            return jsonify({"message": "Project deleted successfully."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

#Ruta 8 Update Project 
from flask import request, jsonify

@app.route('/api/update_project', methods=['POST'])
def update_project():
    try:
        datos = request.json
        project_id = datos.get('project_id')  # Obtener el project_id de los datos de entrada
        project_name = datos.get('project_name')
        description = datos.get('description')
        status = datos.get('status')
        
        # Crear un cursor dentro de la función para tener acceso a él
        cursor = conn.cursor()
        
        # Utilizar parámetros seguros en la consulta SQL
        cursor.execute("UPDATE projects SET project_name = %s, description = %s, status = %s WHERE project_id = %s",
                       (project_name, description, status, project_id))
        conn.commit()

        response = {"message": "Record updated"}
        return jsonify(response), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        # Cerrar el cursor después de usarlo para liberar recursos
        cursor.close()

#Ruta 9 Delete a Task 
@app.route('/api/delete_task/<int:task_id>', methods=['DELETE'])
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

# Ruta 10: Update Task
@app.route('/api/update_task', methods=['POST'])
def update_task():
    try:
        data = request.json
        task_id = data.get('task_id')  # Obtener el task_id de los datos de entrada
        task_name = data.get('task_name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Crear un cursor dentro de la función para tener acceso a él
        cursor = conn.cursor()
        
        # Utilizar parámetros seguros en la consulta SQL
        cursor.execute("UPDATE tasks SET task_name = %s, start_date = %s, end_date = %s WHERE task_id = %s",
                       (task_name, start_date, end_date, task_id))
        conn.commit()

        response = {"message": "Record updated"}
        return jsonify(response), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        # Cerrar el cursor después de usarlo para liberar recursos
        cursor.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
