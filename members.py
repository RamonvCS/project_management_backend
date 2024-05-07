from flask import jsonify, request
import mariadb
from flask import jsonify, request
import mariadb
import sys
from config import DATABASE_CONFIG

conn = mariadb.connect(**DATABASE_CONFIG)

def get_all_members():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM team_members")
        members = cursor.fetchall()
        member_list = []
        for member in members:
            member_dict = {
                "member_id": member[0],
                "name": member[1],
                "email": member[2]
            }
            member_list.append(member_dict)
        return jsonify({"members": member_list}), 200
    except mariadb.Error as e:
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

def update_member(member_id):
    try:
        cursor = conn.cursor()
        
        # Check if member exists
        cursor.execute("SELECT * FROM team_members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()

        if member is None:
            # If member does not exist, return a message and 404 Not Found status
            return jsonify({"error": "Member does not exist."}), 404
        
        # Get updated data from request
        data = request.json
        name = data.get('name')
        email = data.get('email')

        # Update member data
        cursor.execute("UPDATE team_members SET name = %s, email = %s WHERE member_id = %s", (name, email, member_id))
        conn.commit()

        return jsonify({"message": "Member updated successfully."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
