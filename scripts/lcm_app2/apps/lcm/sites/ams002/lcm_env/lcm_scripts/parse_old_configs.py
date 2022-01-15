import os
import json
import shutil
from multiprocessing import Pool
from pol_utils import *
from glob import glob


def parse_old_configs(excel_data, filename):

    """
    list of config files specified in Excel file is parsed. A list of dicts
    containing IP, VLAN and interface data is returned. Each dict represents the
    configuration of a single device. The result is printed in JSON
    format and printed in Excel enabling inspection of data using Excel
    features (i.e.: auto filter).

    :param excel_data: Dict containing data from Excel file
    :param filename: Name of Excel file
    :return: object with configuration data old network elements
    """

    base_dir = os.getcwd()
    old_config_dir = base_dir + '/old_configs'
        
    os.chdir(old_config_dir)
    
    config_files = [configfile for configfile in glob('*cfg*')]
    pool = Pool()
    old_config_data = pool.map(ios_xe_parser, config_files)
    
    os.chdir(base_dir)

    with open('old-configs.json', 'w') as f:
        json.dump(old_config_data, f, indent=4)

    xls_writer(old_config_data, filename)

    return old_config_data
