#!/bin/bash

if test -z "$DJANGOPROJ_HOME"
then
  DJANGOPROJ_HOME=/var/tmp/openaction
  if [ ! -d "$DJANGOPROJ_HOME" ]; then
     echo "ERROR: DJANGOPROJ_HOME is not set and $DJANGOPROJ_HOME does not exist. Exiting"
     exit 1
  fi
  echo "Warning: DJANGOPROJ_HOME is not set, assuming $DJANGOPROJ_HOME"
fi

cd $DJANGOPROJ_HOME

export DJANGOPROJ_HOME
export PYTHONPATH=$DJANGOPROJ_HOME:$PYTHONPATH
export DJANGO_SETTINGS_MODULE=maintenance_settings

function settings_var {
  export name=$1
  (cd $DJANGOPROJ_HOME; (echo "from settings import *"; echo "print $name" ) |python )
}

db_name="$(settings_var 'DATABASES["default"]["NAME"]')"
db_user="$(settings_var 'DATABASES["default"]["USER"]')"
db_pass="$(settings_var 'DATABASES["default"]["PASSWORD"]')"
db_pass="${db_pass:-''}"

read -p "I am going to WIPE DB=$db_name. Are you sure? [y/N]" choice 

if [ "x$choice" == "xy" ]; then

    cat << EOF | python $DJANGOPROJ_HOME/manage.py dbshell --database=super --settings=$DJANGO_SETTINGS_MODULE
\\c postgres
DROP DATABASE $db_name;
create role $db_user  login password $db_pass;
create database $db_name owner $db_user encoding 'utf8' template template0;
grant all privileges on database $db_name to $db_user;
EOF

fi
