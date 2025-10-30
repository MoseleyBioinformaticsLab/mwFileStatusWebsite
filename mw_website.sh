#!/bin/bash
# A Shell Script to update the Metabolomics Workbench File Status website
# Christian D. Powell - 2022/02/20

###########################
# change directory to tmp #
###########################
cd /tmp

###################
# start ssh agent #
###################
eval "$(ssh-agent -s)"
ssh-add /root/.ssh/id_ed25519_github

##############################
# clone  mw file status repo #
##############################
git clone git@github.com:MoseleyBioinformaticsLab/mwFileStatusWebsite.git
cd mwFileStatusWebsite/

###################################################
# install virtualenv and create a new environment #
###################################################
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
python3 -m pip install mwtab
python3 -m pip install -e ../mwFilesStatusWebsite

########################
# update website files #
########################
#python3 -m validator/validator.py
#python3 -m validator/constructor.py
python3 -m mwFileStatusWebsite validate
python3 -m mwFileStatusWebsite generate

###################
# start ssh agent #
###################
eval "$(ssh-agent -s)"
ssh-add /root/.ssh/id_ed25519_github

#############################
# add updated files to repo #
#############################
git add validation_logs index.html missing.html parsing_error.html passing.html validation_error.html warnings_only.html value.html consistency.html format.html
now=$(date +'%Y/%m/%d')
git commit -m "Weekly update for $now"
git push

#####################
# remove everything #
#####################
cd ..
rm -rf mwFileStatusWebsite/
