#################
#### imports ####
#################

import os
import time
import zipfile
import logging
from glob import glob
from utils.utils import login_required, required_access_level, flash_errors
from utils.utils import scripts_wrapper, breadcrumb
from .forms import AddSiteForm, DeleteSiteForm, SelectSiteForm
from .models import Site, db
from flask import Flask, flash, redirect, render_template, Blueprint, current_app
from flask import request, session, url_for, send_file
from werkzeug.utils import secure_filename

lcm = Blueprint('lcm', __name__, template_folder="templates")

def allowed_file(filename):
    return True if filename == 'result.xlsx' else False

#################
# route handlers#
#################

@lcm.route('/lcm')
@login_required
@breadcrumb('LCM')
def lcm_main_menu():
    return render_template('lcm_main_menu.html')


@lcm.route('/lcm/prepare_site')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiding Site')
def lcm_prepare_site_main_menu():
    current_app.logger.info('User %s selected Preparation of a Site', session['username'])
    if session.get('sitename_select'):
        return render_template('lcm_prepare_site_main_menu.html')
    else:
        error = 'U moet eerst een site selecteren'
        current_app.logger.info('User %s forget to select site', session['username'])
        return render_template('lcm_site_mgmt_main_menu.html', error=error)


@lcm.route('/lcm/migrate_site')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Migratie Site')
def lcm_migrate_site_main_menu():
    current_app.logger.info('User %s selected Migration of a Site', session['username'])
    if session.get('sitename_select'):
        return render_template('lcm_migrate_site_main_menu.html')
    else:
        error = 'U moet eerst een site selecteren'
        current_app.logger.info('User %s forget to select site', session['username'])
        return render_template('lcm_site_mgmt_main_menu.html', error=error)


@lcm.route('/lcm/site_mgmt')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Site management')
def lcm_site_mgmt_main_menu():
    current_app.logger.info('User %s selected Migration of a Site', session['username'])
    return render_template('lcm_site_mgmt_main_menu.html')


@lcm.route('/lcm/site_mgmt/add_site', methods=['GET', 'POST'])
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Site management, -> Toevoegen site')
def lcm_add_site():
    form = AddSiteForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            site = Site(name=request.form['sitename'])
            db.session.add(site)
            db.session.commit()
    current_app.logger.info('User %s added a new site', session['username'])
    return render_template('lcm_add_site.html', form=form)


@lcm.route('/lcm/site_mgmt/delete_site', methods=['GET', 'POST'])
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Site management, -> Verwijderen site')
def lcm_delete_site():
    form = DeleteSiteForm(request.form)
    form.sitename.choices = [site.name for site in db.session.query(Site).all()]
    if request.method == 'POST':
        if form.validate_on_submit():
            site = db.session.query(Site).filter(Site.name==request.form['sitename']).first()
            db.session.delete(site)
            db.session.commit()
            flash('Site {} verwijderd'.format(site.name))
            return redirect(url_for('lcm.lcm_main_menu'))
    current_app.logger.info('User %s deleted a site', session['username'])
    return render_template('lcm_delete_site.html', form=form)


@lcm.route('/lcm/site_mgmt/get_sites')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Site management, -> Opvragen sites')
def lcm_get_sites():
    result = []
    sitenames = [site.name for site in db.session.query(Site).all()]
    for sitename in sorted(sitenames):
        row = {'SiteNaam': sitename}
        result.append(row)
    current_app.logger.info('User %s queried the sites', session['username'])
    return render_template('lcm_get_sites.html', result=result)


@lcm.route('/lcm/site_mgmt/select_site',  methods=['GET', 'POST'])
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Site management, -> Selecteren sites')
def lcm_select_site():
    form = DeleteSiteForm(request.form)
    form.sitename.choices = [site.name for site in db.session.query(Site).all()]
    if request.method == 'POST':
        if form.validate_on_submit():
            site = db.session.query(Site).filter(Site.name==request.form['sitename']).first()
            session['sitename_select'] = site.name
            flash('Site {} geselecteerd'.format(site.name))
            current_app.logger.info('User %s selected site %s', session['username'], site.name)
            return redirect(url_for('lcm.lcm_main_menu'))
    return render_template('lcm_select_site.html', form=form)


@lcm.route('/lcm/site_mgmt/create_scripting_env')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Site management, -> Maken scripting omgeving')
def lcm_create_scripting_env():
    sitename = session['sitename_select']
    text = scripts_wrapper('lcm_create_scripting_env', sitename)
    current_app.logger.info('User %s created scripting env', session['username'])
    current_app.logger.info('%s', text)
    return render_template('lcm_script.html', text=text, page='lcm.lcm_main_menu')


@lcm.route('/lcm/prepare_site/download_new_xls')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Download nieuw Excel bestand')
def lcm_download_new_xls():
    current_app.logger.info('User %s downloaded new Excel file', session['username'])
    return send_file('./apps/lcm/new_excel_file/result.xlsx', as_attachment=True)


@lcm.route('/lcm/prepare_site/upload_xls')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Upload Excel bestand')
def lcm_upload_xls():
    return render_template('lcm_upload_xls.html')


@lcm.route('/lcm/prepare_site/xls_uploader', methods = ['GET', 'POST'])
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Upload Excel bestand')
def lcm_xls_uploader():
    if request.method == 'POST':
        curr_dir = os.getcwd()
        sitename = session['sitename_select']
        os.chdir('./apps/lcm/sites/' + sitename + '/lcm_env')
        current_app.logger.info('User %s uploaded an Excel file', session['username'])
        f = request.files['file']
        f.save(secure_filename(f.filename))
        flash('Bestand geupload')
        os.chdir(curr_dir)
        return render_template('lcm_prepare_site_main_menu.html')
    

@lcm.route('/lcm/prepare_site/download_current_xls')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Download bestaand Excel bestand')
def lcm_download_current_xls():
    sitename = session['sitename_select']
    filename = './apps/lcm/sites/' + sitename + '/results/result.xlsx' 
    current_app.logger.info('User %s downloaded an Excel file', session['username'])
    return send_file(filename, as_attachment=True)


@lcm.route('/lcm/prepare_site/lcm_old_inventory')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Maken ansible inventory oude site')
def lcm_old_inventory():
    sitename = session['sitename_select']
    text = scripts_wrapper('lcm_old_inventory', sitename)
    current_app.logger.info('User %s created old inventory', session['username'])
    current_app.logger.info('%s', text)
    session['old_inventory'] = True
    return render_template('lcm_script.html', text=text, page='lcm.lcm_prepare_site_main_menu')


@lcm.route('/lcm/prepare_site/backup')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Maken backup configuraties')
def lcm_backup():
    sitename = session['sitename_select']
    if session.get('old_inventory'):
        session['backups_made'] = True
        text = scripts_wrapper('lcm_backup', sitename)
        current_app.logger.info('User %s backup old configs', session['username'])
        current_app.logger.info('%s', text)
    else:
        error = 'U moet eerst de Ansible inventory van de bestaande machines maken'
        current_app.logger.info('User %s forget to select inventory', session['username'])
        return render_template('lcm_prepare_site.html', error=error)
    return render_template('lcm_script.html', text=text, page='lcm.lcm_prepare_site_main_menu')


@lcm.route('/lcm/prepare_site/generate')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Genereren configuraties')
def lcm_generate():
    if session.get('backups_made'):
        sitename = session['sitename_select']
        session['configs_generated'] = True
        text = scripts_wrapper('lcm_generate', sitename)
        current_app.logger.info('User %s created new configs', session['username'])
        current_app.logger.info('%s', text)
        return render_template('lcm_script.html', text=text, page='lcm.lcm_prepare_site_main_menu')
    else:
        error = 'U moet eerst backups van de bestaande machines maken'
        current_app.logger.info('User %s forget to backup configs', session['username'])
        return render_template('lcm_prepare_site_main_menu.html', error=error)


@lcm.route('/lcm/prepare_site/download_cfgs')
@login_required
@required_access_level('lcm_user')
@breadcrumb('LCM, -> Voorbereiden migratie, -> Downloaden configuraties')
def lcm_download_cfgs():
    sitename = session['sitename_select']
    curr_dir = os.getcwd()
    os.chdir('./apps/lcm/sites/' + sitename + '/lcm_env/lcm_configs')
    file_dir = os.getcwd()
    filenames = [filename for filename in glob('*.txt')]
    os.chdir(curr_dir)
    current_app.logger.info('User %s downloaded configs', session['username'])
    with zipfile.ZipFile('all.zip','w', zipfile.ZIP_DEFLATED) as zf:
        for filename in filenames:
            zf.write(os.path.join(file_dir, filename))
    return send_file('all.zip', mimetype = 'zip', attachment_filename= 'all.zip', as_attachment = True)


@lcm.route('/lcm/migrate_site/save_state_info')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Migratie site, -> Opslaan netwerktabellen')
def lcm_save_state_info():
    sitename = session['sitename_select']
    text = scripts_wrapper('lcm_save_state_info', sitename)
    current_app.logger.info('User %s saved state from old site', session['username'])
    current_app.logger.info('%s', text)
    return render_template('lcm_script.html', text=text, page='lcm.lcm_migrate_site_main_menu')


@lcm.route('/lcm/migrate_site/dynamic_inventory')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Migratie site, -> Maken ansible inventory')
def lcm_dynamic_inventory():
    session['dyn_inv_created'] = True
    sitename = session['sitename_select']
    text = scripts_wrapper('lcm_dynamic_inventory', sitename)
    current_app.logger.info('User %s created a dynamic inventory', session['username'])
    current_app.logger.info('%s', text)
    return render_template('lcm_script.html', text=text, page='lcm.lcm_migrate_site_main_menu')


@lcm.route('/lcm/migrate_site/push_initial_cfg')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Migratie site, -> Pushen initiele configuraties')
def lcm_push_initial_cfg():
    if session.get('dyn_inv_created'):
        session['dyn_inv_created'] = False
        sitename = session['sitename_select']
        text = scripts_wrapper('lcm_push_initial_cfg', sitename)
        current_app.logger.info('User %s pushed an initial config', session['username'])
        current_app.logger.info('%s', text)
        return render_template('lcm_script.html', text=text, page='lcm.lcm_migrate_site_main_menu')
    else:
        error = 'U moet eerst een dynamische inventory maken'
        current_app.logger.info('User %s forget to generate dynamic inventory', session['username'])
        return render_template('lcm_main_menu.html', error=error)


@lcm.route('/lcm/migrate_site/push_aaa_cfg')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Migratie site, -> Pushen AAA configuraties')
def lcm_push_aaa_cfg():
    if session.get('dyn_inv_created'):
        session['dyn_inv_created'] = False
        sitename = session['sitename_select']
        text = scripts_wrapper('lcm_push_aaa_cfg', sitename)
        current_app.logger.info('User %s pushed an AAA config', session['username'])
        current_app.logger.info('%s', text)
        return render_template('lcm_script.html', text=text, page='lcm.lcm_migrate_site_main_menu')
    else:
        error = 'U moet eerst een dynamische inventory maken'
        current_app.logger.info('User %s forget to generate dynamic inventory', session['username'])
        return render_template('lcm_main_menu.html', error=error)


@lcm.route('/lcm/migrate_site/push_final_cfg')
@login_required
@required_access_level('lcm_superuser')
@breadcrumb('LCM, -> Migratie site, -> Pushen finale configuraties')
def lcm_push_final_cfg():
    sitename = session['sitename_select']
    text = scripts_wrapper('lcm_push_final_cfg', sitename)
    current_app.logger.info('User %s pushed a final config', session['username'])
    current_app.logger.info('%s', text)
    return render_template('lcm_script.html', text=text, page='lcm.lcm_migrate_site_main_menu')
