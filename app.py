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

# Ruta 1: Retrieve all projects from the database
@app.route('/api/projects', methods=['GET'])
def projects():
    cursor = conn.cursor()
    cursor.execute("SELECT project_name, description, project_id, status FROM projects")
    result = cursor.fetchall()
    cursor.close()

    projects = [ProjectDTO(project_name=row[0], description=row[1], project_id=row[2], status=row[3]).to_dict() for row in result]

    response = jsonify({'projects': projects})
    response.headers.add("Access-Control-Allow-Origin", '*')
    return response

class ProjectDTO:
    def __init__(self, project_name, description, project_id, status):
        self.project_name = project_name
        self.description = description
        self.project_id = project_id
        self.status = status

    def to_dict(self):
        return {
            'project_name': self.project_name,
            'description': self.description,
            'project_id': self.project_id,
            'status': self.status
        }

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
        tasks_list = []
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            if tasks:
                for task in tasks:
                    tasks_list.append({
                        "task_name": task[1],  # Cambiado de task[0] a task[1]
                        "start_date": task[2],
                        "end_date": task[3]
                    })
            else:
                return jsonify({"message": "No tasks found"}), 404  # No necesitas el project_id aquí
        response = jsonify({"data": tasks_list})
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
