from flask import Flask, flash, render_template, request, redirect, url_for, \
                  make_response, session, get_flashed_messages
import json

app = Flask(__name__)
app.secret_key = "secret_key"


@app.route('/')
def hello_world():
    return 'Welcome to Flask!'


@app.errorhandler(404)
def not_found(error):
    return 'Oops!', 404


def load_users():
    try:
        users = json.loads(request.cookies.get('users', json.dumps([])))
    except:
        with open('hexlet-flask-example/templates/users/users.json', 'a') as f:
            users = json.loads(f.read())
    return users


@app.route('/users/<int:id>')
def get_users(id):
    users = load_users()
    for user in users:
        if user['id'] == str(id):
            return render_template(
                '/users/show.html',
                user=user,
            )
    return 'Page not found!', 404


def validate(user):
    errors = {}
    if len(user['name']) < 4:
        errors['name'] = 'Nickname must be greater than 4 characters'
    if len(user['email']) < 4:
        errors['email'] = 'Email must be greater than 4 characters'
    return errors


@app.route('/users')
def search_user():
    term = request.args.get('term', '', type=str)
    messages = get_flashed_messages(with_categories=True)
    users = load_users()
    filtered_users = []
    for user in users:
        pattern = user['name']
        if term == pattern[:len(term)]:
            filtered_users.append(user)
    return render_template(
        'users/index.html',
        messages=messages,
        users=filtered_users,
        search=term
    )


@app.route('/users/new')
def users_new():
    user = {'id': '',
            'name': '',
            'email': ''}
    errors = {}
    return render_template(
        'users/new.html',
        user=user,
        errors=errors
        )


@app.post('/users')
def users_post():
    users = load_users()
    user = request.form.to_dict()
    errors = validate(user)
    if errors:
        return render_template(
            'users/new.html',
            user=user,
            errors=errors
        ), 422
    if users:
        user['id'] = str(int(users[-1]['id'])+1)
    else:
        user['id'] = str(0)
    users.append(user)
    flash('User was added successfully', 'success')
    encoded_users = json.dumps(users)
    response = make_response(redirect(url_for('search_user')))
    response.set_cookie('users', encoded_users)
    return response


@app.route('/users/<id>/edit')
def edit_user(id):
    users = load_users()
    selected_user = {}
    for user in users:
        if user['id'] == str(id):
            selected_user = user
    errors = {}
    return render_template(
        'users/edit.html',
        user=selected_user,
        errors=errors,
    )


@app.route('/users/<id>/edit', methods=['POST'])
def patch_user(id):
    users = load_users()
    for user in users:
        if user['id'] == str(id):
            user=user
            break
    data = request.form.to_dict()
    errors = validate(data)
    if errors:
        return render_template(
            'users/edit.html',
            user=user,
            errors=errors,
        ), 422
    user['name'] = data['name']
    user['email'] = data['email']
    flash('User has been updated', 'success')
    encoded_users = json.dumps(users)
    response = make_response(redirect(url_for('search_user')))
    response.set_cookie('users', encoded_users)
    return response


@app.route('/users/<id>/delete', methods=['POST'])
def delete_user(id):
    users = load_users()
    for user in users:
        if user['id'] == str(id):
            users.remove(user)
    flash('User has been deleted', 'success')
    encoded_users = json.dumps(users)
    response = make_response(redirect(url_for('search_user')))
    response.set_cookie('users', encoded_users)
    return response


@app.route('/login', methods=['POST', 'GET'])
def user_login():
    session_status = 0
    users = load_users()
    email = request.args.get('email', '', type=str)
    session['users'] = []
    for user in users:
        print(f"{user['email']} {email}")
        if str(email) == user['email']:
            session['users'].append(user)
            session_status = 1
            flash('User is successfully logged in', 'success')
            return redirect(url_for('search_user'))
    return render_template(
                'users/login.html',
                emal=email,
    )
