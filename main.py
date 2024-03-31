
from flask import Flask, request, jsonify, Response, session, flash, redirect, url_for, render_template, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from dotenv import load_dotenv
import os, datetime

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


#--------------------------------------------------------------------------------------
# environment variables / constants
#--------------------------------------------------------------------------------------

HOST='::'
PORT=8082

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
ADMIN_NAME = os.getenv('ADMIN_NAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)  
DB_URI = os.getenv('DB_URI')

database.init_db(DB_URI)

#--------------------------------------------------------------------------------------
# helper functions
#--------------------------------------------------------------------------------------

with open('static/favicon.ico', 'rb') as f:
    favicon_data = f.read()


def set_admin_cookie(response):
    expiration = datetime.datetime.now() + datetime.timedelta(days=30)
    response.set_cookie('admin_cookie', 'true', domain='.overburn.dev', expires=expiration)
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
        if username == ADMIN_NAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            response = make_response(redirect(url_for('admin_sql')))
            return set_admin_cookie(response)
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


@app.after_request
def after_request(response):
    page_route = request.path
    if page_route != '/create':
        database.track_page(request, response)
    return response


@app.errorhandler(404)
def page_not_found(e):
    path = request.path
    return f"404: The requested path '{path}' was not found.", 404


#--------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)