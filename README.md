#### Upgrade pip and install virtualenv
python3 -m pip install --user --upgrade pip\
python3 -m pip install --user virtualenv

#### Make virtualenv named env
python3 -m venv env

#### Activate the environment env
source env/bin/activate

#### Then install this library 
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

#### Run scripts
python3 foo.py