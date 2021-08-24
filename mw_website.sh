#!/bin/bash
# A Shell Script to update the Metabolomcis Workbench File Status website
# Christian D. Powell - 21/Aug/2021

###########################
# change directory to tmp #
###########################
cd /tmp

##############################
# clone  mw file status repo #
##############################
git clone https://github.com/cdpowell/test-project.git
cd test-project/

###################################################
# install virtualenv and create a new environment #
###################################################
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
python3 -m install mwtab

########################
# update website files #
########################
python3 -m validator/validator.py
python3 -m validator/generate_html.py

#############################
# add updated files to repo #
#############################
git add docs/validation_logs index.html missing.html parsing_error.html passing.html validation_error.html
git commit -m "Weekly update to website."
git push

#####################
# remove everything #
#####################
cd ..
rm -rf test-project/