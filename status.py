import os
import json
from glob import glob

curr_dir = os.getcwd()
status_dir = curr_dir + "/status"

os.chdir(status_dir)

hostnamefiles = [filename for filename in glob('*.txt')]

try:
    with open('hosts_done.json', 'r') as f:
        hosts_done = json.load(f)
except:
    hosts_done = []

for filename in hostnamefiles:
    with open(filename, 'r') as lines:
        for line in lines:
            hosts_done.append(line)
    os.remove(filename)

with open('hosts_done.json', 'w') as f:
    json.dump(hosts_done, f, indent=4)
