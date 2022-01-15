import os
import shutil
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="LCM scripting environmenmt builder"
    )
    parser.add_argument('-D', '--dest',
                        dest='dest',
                        help='Destination root directory',
                        type=str
    )
    parser.add_argument('-S', '--sitename',
                        dest='sitename',
                        help='Sitename',
                        type=str
    )
    return parser.parse_args()


def create_scripting_env():

    args = parse_args()
    dest_dir = args.dest
    sitename = args.sitename

    curr_dir = os.getcwd()
    sites_root_dir = dest_dir + '/sites/'
    if not os.path.isdir(sites_root_dir + sitename):
        print('New root directory for site created')
        os.mkdir(sites_root_dir + sitename)

    lcm_env_dir = sites_root_dir + sitename + '/lcm_env'
    if os.path.isdir(lcm_env_dir):
        shutil.rmtree(lcm_env_dir)
    shutil.copytree(curr_dir, lcm_env_dir)
    print('LCM scripting environment created')


if __name__ == "__main__":
    create_scripting_env()
