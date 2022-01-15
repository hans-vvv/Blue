#################
#### imports ####
#################

import os
import time
import logging
import concurrent.futures
from utils.utils import login_required, required_access_level, flash_errors, breadcrumb
from .forms import LoginForm, AddUserForm, AddUserAuthForm
from .models import User, UserRole, db
from flask import Flask, flash, redirect, render_template, Blueprint, current_app
from flask import request, session, url_for, send_file, g

admin = Blueprint('admin', __name__, template_folder="templates")


def allowed_file(filename):
    return True if filename == 'result.xlsx' else False

#################
# route handlers#
#################

@admin.route('/')
def index():
    session.clear()
    return render_template('index.html')


@admin.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).filter_by(name=request.form['username']).first()
            if user is not None and user.password == request.form['password']:
                session.clear()
                userroles = db.session.query(UserRole).filter(UserRole.users.any(id=user.id)).all()
                user_rolenames = [userrole.name for userrole in userroles]
                current_app.logger.info('User %s logged in', user.name)
                session['username'] = user.name
                session['logged_in'] = True
                session['user_rolenames'] = user_rolenames
                flash('U bent ingelogd!')
                return redirect(url_for('admin.main_menu'))
            else:
                current_app.logger.error('Invalid username or password.')
                error = 'Invalid username or password.'
                return render_template('login.html', error=error, form=form,)
    return render_template('login.html', error=error, form=form)


@admin.route('/main_menu')
@login_required
def main_menu():
    return render_template('main_menu.html')


@admin.route('/admin')
@login_required
@required_access_level('admin')
@breadcrumb('Admin')
def admin_menu():
    current_app.logger.info('User %s logged into the admin main page', session['username'])
    return render_template('admin_menu.html')


@admin.route('/admin/add_user/', methods=['GET', 'POST'])
@login_required
@required_access_level('admin')
@breadcrumb('Admin, -> Gebruiker toevoegen')
def add_user():
    form = AddUserForm(request.form)
    form.userrole.choices = [userrole.name for userrole in db.session.query(UserRole).all()]
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(name=request.form['username'], password='Welkom123!')
            db.session.add(user)
            userrole = db.session.query(UserRole).filter(UserRole.name==request.form['userrole']).first()
            userrole.users.append(user)
            db.session.commit()
    current_app.logger.info('User %s added a new user', session['username'])
    return render_template('add_user.html', form=form)


@admin.route('/admin/get_users/', methods=['GET', 'POST'])
@login_required
@required_access_level('admin')
@breadcrumb('Admin, -> Gebruikers opvragen')
def get_users():
    result = []
    for user in db.session.query(User).all():
        userroles = db.session.query(UserRole).filter(UserRole.users.any(id=user.id)).all()
        user_rolenames = [userrole.name for userrole in userroles]
        row = {'Gebruikers': user.name, 'Gebruikersrollen': ','.join(user_rolenames)}
        result.append(row)
    current_app.logger.info('User %s queried all users', session['username'])
    return render_template('get_users.html', result=result)


@admin.route('/admin/add_user_auth/', methods=['GET', 'POST'])
@login_required
@required_access_level('admin')
@breadcrumb('Admin, -> Gebruikers authorisatie toevoegen')
def add_user_auth():
    form = AddUserAuthForm(request.form)
    form.username.choices = [user.name for user in db.session.query(User).all()]
    form.userrole.choices = [userrole.name for userrole in db.session.query(UserRole).all()]
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).filter(User.name==request.form['username']).first()
            userrole = db.session.query(UserRole).filter(UserRole.name==request.form['userrole']).first()
            userrole.users.append(user)
            db.session.commit()
    current_app.logger.info('User %s added authorization to a user', session['username'])
    return render_template('add_user_auth.html', form=form)
