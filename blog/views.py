# -*- coding: utf-8 -*-

from models import User, get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    posts = get_todays_recent_posts()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            flash(u'Su nombre de usuario debería tener por lo menos un carácter.')
        elif len(password) < 5:
            flash(u'Su contraseña debería tener por lo menos cinco caractéres.')
        elif not User(username).register(password):
            flash(u'Ya existe un usuario con ese nombre.')
        else:
            session['username'] = username
            flash(u'Ya entró.')
            return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash(u'Entrada invalida.')
        else:
            session['username'] = username
            flash(u'Ya entró.')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash(u'Ya salió.')
    return redirect(url_for('index'))

@app.route('/add_post', methods=['POST'])
def add_post():
    title = request.form['title']
    tags = request.form['tags']
    text = request.form['text']

    if not title or not tags or not text:
        if not title:
            flash(u'Debes proveer un título a su mensaje.')
        if not tags:
            flash(u'Debes proveer por lo menos una etiqueta a su mensaje.')
        if not text:
            flash(u'Debes escribir un mensaje.')
    else:
        User(session['username']).add_post(title, tags, text)

    return redirect(url_for('index'))

@app.route('/like_post/<post_id>')
def like_post(post_id):
    username = session.get('username')

    if not username:
        flash(u'Debes de entrar al sitio para poder dar un "Me gusta".')
        return redirect(url_for('login'))

    User(username).like_post(post_id)

    flash(u'Me gusta.')
    return redirect(request.referrer)

@app.route('/follow/<followed_username>')
def follow_user(followed_username):
    username = session.get('username')

    if not username:
        flash(u'Debes de entrar al sitio para poder seguir a este usuario.')
        return redirect(url_for('login'))

    User(username).follow_user(followed_username)

    flash(u'Estás siguiendo a ' + followed_username + '.')
    return redirect(url_for('profile', username=followed_username))

@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = User(user_being_viewed_username)
    posts = user_being_viewed.get_recent_posts()

    similar = []
    already_followed = False
    common = []

    if logged_in_username:
        logged_in_user = User(logged_in_username)

        if logged_in_user.username == user_being_viewed.username:
            similar = logged_in_user.get_similar_users()
        else:
            already_followed = logged_in_user.is_following(user_being_viewed_username)
            common = logged_in_user.get_commonality_of_user(user_being_viewed)

    return render_template(
        'profile.html',
        username=username,
        posts=posts,
        similar=similar,
        already_followed=already_followed,
        common=common
    )