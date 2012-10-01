#!/usr/bin/python

import sys, os, shutil

script_path = os.path.abspath(__file__)

oa_path =  os.path.sep.join(script_path.split(os.path.sep)[:-2])

migration_file = '0001_openaction_askbot_extensions.py'

migration_path_from = oa_path + '/openaction/askbot_extensions/migrations/' + migration_file

migration_path_to = oa_path + '/submodules/askbot-devel/askbot/migrations/'

migration_files = os.listdir(migration_path_to)

max_name = 0

for file in migration_files:
    name = file[:4]
    try:
        name = int(name)
        if(name>max_name):
            max_name = name
    except ValueError:
        pass

max_name += 1

max_name = str(max_name).zfill(4)

migration_path_to = migration_path_to + max_name + (migration_file[4:])

shutil.copy(migration_path_from, migration_path_to)
