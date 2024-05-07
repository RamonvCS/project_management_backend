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

  # Ruta 1: Create a new task for a specific member
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

#ruta 2 Delete_member
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
 