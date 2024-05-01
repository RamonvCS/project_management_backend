from flask import Flask, jsonify
import mariadb
import sys
from config import DATABASE_CONFIG

app = Flask(__name__)

try:
    conn = mariadb.connect(**DATABASE_CONFIG)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

cursor = conn.cursor()

#Ruta 1 para llamar la tabla de projects de la base datos de project_management
@app.route('/api/projects', methods=['GET'])
def projects():
    cursor.execute("SELECT project_name, description, status from projects")
    projects = cursor.fetchall()
    # Convert the results into a more friendly format or return them directly
    return jsonify({'projects': projects})

#Ruta 2 para llamar la tabla de ______ de la base datos de project_management

# @app.route('/api/_______-', methods=['GET'])
# def projects():
#     cursor.execute("SELECT project_name, description, status from projects")
#     projects = cursor.fetchall()
#     # Convert the results into a more friendly format or return them directly
#     return jsonify({'projects': projects})

#Ruta 3 para llamar la tabla de ______ de la base datos de project_management

# @app.route('/api/_______-', methods=['GET'])
# def projects():
#     cursor.execute("SELECT project_name, description, status from projects")
#     projects = cursor.fetchall()
#     # Convert the results into a more friendly format or return them directly
#     return jsonify({'projects': projects})

#Ruta 4 para llamar la tabla de ______ de la base datos de project_management

# @app.route('/api/_______-', methods=['GET'])
# def projects():
#     cursor.execute("SELECT project_name, description, status from projects")
#     projects = cursor.fetchall()
#     # Convert the results into a more friendly format or return them directly
#     return jsonify({'projects': projects})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
