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
@app.route('/api/new_task/<int:member_id>', methods=['POST'])
def new_task(member_id):
    data = request.json
    task_name = data.get('task_name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task_name, start_date, end_date, member_id) VALUES (?, ?, ?, ?)", (task_name, start_date, end_date, member_id))
        conn.commit()
        return jsonify({"message": "New task created successfully"}), 201
    except mariadb.Error as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
