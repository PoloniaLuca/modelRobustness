#!/bin/bash

if cd ~/cache/; then git add .; git reset --hard; GIT_LFS_SKIP_SMUDGE=1 git pull; else git clone git@github-dss:riccardoangius/DSS-quality-assessment-apps.git ~/cache; fi

COMMIT_ID=$(git log --pretty=format:'%h' -n 1)

TOOLNAME=$(echo `whoami` | tr '[:upper:]' '[:lower:]')

[ -d ~/mysite.prevdeploy ] &&  rm -rf ~/mysite.prevdeploy

[ -d ~/mysite ] &&  mv ~/mysite ~/mysite.prevdeploy

[ -d ~/mysite.prevdeploy/static/output1 ] &&  rm -rf ~/mysite.prevdeploy/static/output1
[ -d ~/mysite.prevdeploy/static/output2 ] &&  rm -rf ~/mysite.prevdeploy/static/output2
[ -d ~/mysite.prevdeploy/static/output3 ] &&  rm -rf ~/mysite.prevdeploy/static/output3

cp -r ~/cache/$TOOLNAME/mysite ~/mysite

cp -nr ~/cache/common/* ~/mysite/

echo "<!-- $COMMIT_ID --> " >> ~/mysite/templates/home.html

RAW_PYVERSION=`cat ~/mysite/runtime.txt`
PIPVERSION=pip${RAW_PYVERSION#"python-"}

cd ~/mysite && $PIPVERSION install -r requirements.txt

# Trigger app reload
touch /var/www/${TOOLNAME}_pythonanywhere_com_wsgi.py