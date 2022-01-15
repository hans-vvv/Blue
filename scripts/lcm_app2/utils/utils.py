import os
import re
import shutil
import subprocess
from collections import namedtuple
from flask import session, flash, redirect, url_for, g, request
from functools import wraps


def create_breadcrumbs(path):
    result = []
    m = re.search('^\/\w+', path)
    if m:
        result.append(m.group(0))
    m = re.search('^\/\w+\/\w+', path)
    if m:
        result.append(m.group(0))
    m = re.search('^\/\w+\/\w+\/\w+', path)
    if m:
        result.append(m.group(0))
    return result


def breadcrumb(view_title):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            g.breadcrumbs = create_breadcrumbs(request.path)
            g.breadcrumb_titles = view_title.split(',') 

            # Call the view
            route_view = f(*args, **kwargs)

            return route_view
        return decorated_function
    return decorator


def login_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if session.get('logged_in'):
            return func(*args, **kwargs)
        else:
            flash('U moet eerst inloggen.')
            return redirect(url_for('admin.login'))
    return wrap


def required_access_level(access_level):
    def decorator(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            if access_level not in session.get('user_rolenames'):
                flash('U bent niet geautoriseerd.')
                return redirect(url_for('admin.main_menu'))
            else:
                return func(*args, **kwargs)
        return wrap
    return decorator


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error), 'error')


def allowed_file(filename):
    return True if filename == 'result.xlsx' else False


def scripts_wrapper(selection, sitename):
    curr_dir = os.getcwd()
    if selection == 'lcm_create_scripting_env':
        os.chdir('../lcm_env')
        dest_dir = curr_dir + '/apps/lcm/'
        fmt = 'python3 create_scripting_env.py -D "{}" -S "{}"'.format(dest_dir, sitename)
        cmd = subprocess.getoutput(fmt)
        os.chdir(curr_dir)
    elif selection == 'lcm_old_inventory':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env' +  '/ansible/')
        cmd = subprocess.getoutput("ansible-playbook 10-lcm-create-old_inventory.yml")
        os.chdir(curr_dir)
    elif selection == 'lcm_backup':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env' +  '/ansible/')
        cmd = subprocess.getoutput("ansible-playbook 11-lcm-backup-old_configs.yml")
        os.chdir(curr_dir)
    elif selection == 'lcm_generate':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env')
        cmd = subprocess.getoutput("python3 config_generator.py")
        os.chdir(curr_dir)
    elif selection == 'lcm_save_state_info':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env' +  '/ansible/')
        cmd = subprocess.getoutput("ansible-playbook 30-lcm-get_network_state_old_configs.yml")
        os.chdir(curr_dir)
    elif selection == 'lcm_dynamic_inventory':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env' +  '/ansible/')
        cmd = subprocess.getoutput("ansible-playbook 40-lcm-create-dynamic_inventory.yml")
        os.chdir(curr_dir)
    elif selection == 'lcm_push_initial_cfg':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env' +  '/ansible/')
        cmd = subprocess.getoutput("ansible-playbook 41-lcm-push-initial_configs.yml")
        os.chdir(curr_dir)
    elif selection == 'lcm_push_aaa_cfg':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env' +  '/ansible/')
        cmd = subprocess.getoutput("ansible-playbook 42-lcm-push-aaa_configs.yml")
        os.chdir(curr_dir)
    elif selection == 'lcm_push_final_cfg':
        os.chdir(curr_dir + '/apps/lcm/sites/' + sitename + '/lcm_env' +  '/ansible/')
        cmd = subprocess.getoutput("ansible-playbook 50-lcm-push-final_configs.yml")
        os.chdir(curr_dir)
    return cmd
