
from flask import Flask, request, jsonify, Response, session, flash, redirect, url_for, render_template, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from dotenv import load_dotenv
import os

import database

app = Flask(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        else:
            flash('You need to be logged in to view this page.')
            return redirect(url_for('admin_login'))
    return decorated_function

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
admin_username = os.getenv('ADMIN_NAME')
admin_password = os.getenv('ADMIN_PASSWORD')
admin_password_hash = generate_password_hash(admin_password)  
db_uri = os.getenv('DB_URI')
database.init_db(db_uri)

#--------------------------------------------------------------------------------------
# helper functions
#--------------------------------------------------------------------------------------

with open('static/favicon.ico', 'rb') as f:
    favicon_data = f.read()

def set_admin_cookie():
    response = make_response("Cookie set")
    response.set_cookie('admin_cookie', 'true')
    return response

#--------------------------------------------------------------------------------------
# sql routes
#--------------------------------------------------------------------------------------

@app.route('/create', methods=['POST'])
def create_page_hit():

    req_data = request.get_json()

    is_valid, reason = database.validate_data(req_data)
    if not is_valid:
        return jsonify({'error': reason}), 400
    
    database.add(req_data)
    return jsonify({'message': 'Page hit created successfully'}), 201


@app.route('/sql', methods=['POST'])
@admin_required
def execute_sql_query():
    data = request.json
    raw_text = data.get('query', '')

    if not raw_text:
        return jsonify({'error': 'Missing query text'}), 400

    try:
        result = database.query(raw_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#--------------------------------------------------------------------------------------
# admin routes
#--------------------------------------------------------------------------------------

@app.route('/')
@admin_required
def admin_sql():
    return render_template('admin_sql.html')

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('admin_sql'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_username and check_password_hash(admin_password_hash, password):
            session['logged_in'] = True
            set_admin_cookie() 
            return redirect(url_for('admin_sql'))
        else:
            flash('Invalid credentials')
    return render_template('admin_login.html')  # Your login page template

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

#--------------------------------------------------------------------------------------

@app.route('/favicon.ico')
def favicon():
    return Response(favicon_data, mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def page_not_found(e):
    path = request.path
    return f"404: The requested path '{path}' was not found.", 404

#--------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)