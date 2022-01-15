#!/usr/bin/python3
import sys
sys.path.insert(0, '/var/www/html/lcm_app2')
from lcm_app2 import create_app
application = create_app()
