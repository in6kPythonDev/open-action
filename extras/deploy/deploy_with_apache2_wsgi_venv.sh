#!/bin/bash

echo "Use absolute paths"

while [ ! -d $dir_oa_project ]; do
    read dir_oa_project -p "OpenAction installation directory: "
done

while [ ! -d $dir_venv ]; do
    read dir_venv -p "Base directory of your virtualenv: "
done

while [ ! -d $dir_cgi ]; do
    read dir_venv -p "Web server executable directory: "
done

#TODO ric: aggiungere anche yoursite.com

function settings_var {
  export name=$1
  (cd $dir_oa_project; (echo "from settings import *"; echo "print $name" ) | python )
}

web_path="$(settings_var 'ASKBOT_URL')"

sed "s@OA_DEPLOY_DIR@$dir_oa_project@g" oa.apache2.dist | \
    sed "s@OA_WEB_DIR@$askbot_url@g" | \
    sed "s@YOUR_CGI_PATH@$dir_cgi@g" > oa.apache2

dir_pyvenv_sitepkgs=`ls -ld $dir_venv/lib/python*/site-packages/`
module_name="`basename $dir_oa_project`.settings"

sed "s@^VIRTUALENVDIR =.*@VIRTUALENVDIR = $dir_venv@g" django_venv.wsgi.dist | \
    sed "s@^ALLDIRS =.*@ALLDIRS = [\"$dir_pyvenv_sitepkgs\"]@g" | \
    sed "s@^module_name =.*@module_name = $module_name" > django_venv.wsgi

    

