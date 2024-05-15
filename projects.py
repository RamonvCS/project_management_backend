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

#------------------------------------** FUNCION NEW PROJECT **----------------------------------------
def new_project():
    conn = get_db_connection()
    try:
        data = request.json
        project_name = data.get('project_name')
        description = data.get('description')
        status = data.get('status')

        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (project_name, description, status) VALUES (?, ?, ?)", (project_name, description, status))
        conn.commit()
        return jsonify({"message": "Project inserted successfully"}), 201
    
    except mariadb.Error as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()

#------------------------------------** FUNCION DELETE PROJECT **----------------------------------------
def delete_project(project_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if project exists
        cursor.execute("SELECT * FROM projects WHERE project_id = %s", (project_id,))
        project = cursor.fetchone()

        if project is None:
            return jsonify({"error": "Project does not exist."}), 404
        
        # Check if project is associated with any tasks
        cursor.execute("SELECT * FROM tasks WHERE project_id = %s", (project_id,))
        tasks = cursor.fetchall()
        
        cursor.execute("SELECT * FROM team_members WHERE project_id = %s", (project_id,))
        members = cursor.fetchall()

        if tasks:
            return jsonify({"error": "Cannot delete project as it is associated with tasks."}), 400
        elif members:
            return jsonify({"error": "Cannot delete project as it is associated with members."}), 400
        else:
            cursor.execute("DELETE FROM projects WHERE project_id = %s", (project_id,))
            conn.commit()
            return jsonify({"message": "Project deleted successfully."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#------------------------------------** FUNCION UPDATE PROJECT **----------------------------------------
def update_project(project_id):
    conn = get_db_connection()
    try:
        data = request.json
        project_name = data.get('project_name')
        description = data.get('description')
        status = data.get('status')
        
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET project_name = %s, description = %s, status = %s WHERE project_id = %s",
                       (project_name, description, status, project_id))
        conn.commit()

        return jsonify({"message": "Record updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#------------------------------------** FUNCION GET ALL PROJECTS **----------------------------------------
def get_all_projects():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
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
        conn.close()
