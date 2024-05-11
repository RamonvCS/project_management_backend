from flask import Flask, jsonify, request
import mariadb
import sys
from flask_cors import CORS
from config import DATABASE_CONFIG
from tasks import create_task, delete_task, get_all_tasks, update_task
from members import get_all_members, delete_member, update_member, add_members, get_members_by_project
from projects import new_project, delete_project, update_project, get_all_projects

app = Flask(__name__)
CORS(app)

#-----------------------------** RUTAS DE TAREAS **---------------------------------------
@app.route('/api/new_task/<int:project_id>/<int:member_id>', methods=['POST'])
def new_task_route(project_id, member_id):
    return create_task(project_id, member_id)

@app.route('/api/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task_route(task_id):
    return delete_task(task_id)

@app.route('/api/get_all_tasks', methods=['GET'])
def get_all_tasks_route():
    return get_all_tasks()

@app.route('/api/update_task/<int:task_id>', methods=['POST'])
def update_task_route(task_id):
    return update_task(task_id)

#-----------------------------** RUTAS DE MIEMBROS **-------------------------------------
@app.route('/api/get_all_members', methods=['GET'])
def get_all_members_route():
    return get_all_members()

@app.route('/api/delete_member/<int:member_id>', methods=['DELETE'])
def delete_member_route(member_id):
    return delete_member(member_id)

@app.route('/api/update_member/<int:member_id>', methods=['POST'])
def update_member_route(member_id):
    return update_member(member_id)


#Abielmelex#
@app.route('/api/add_members/<int:project_id>/<int:member_id>', methods=['POST'])
def add_member_route(project_id, member_id):
    return add_members(project_id, member_id)

@app.route('/api/get_members_by_project/<int:project_id>', methods=['GET'])
def get_members_by_project_route(project_id):
    # Llama a la función que contiene la lógica de la base de datos
    return get_members_by_project(project_id)   

#-----------------------------** RUTAS DE PROYECTOS **------------------------------------
@app.route('/api/new_project', methods=['POST'])  # Ruta para crear un nuevo proyecto
def new_project_route():
    return new_project() 

@app.route('/api/delete_project/<int:project_id>', methods=['DELETE'])
def delete_project_route(project_id):
    return delete_project(project_id)

@app.route('/api/update_project/<int:project_id>', methods=['POST'])
def update_project_route(project_id):
    return update_project(project_id)

@app.route('/api/get_all_projects', methods=['GET'])
def get_all_projects_route():
    return get_all_projects()

#------------------------------------** RUTAS END **----------------------------------------


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
