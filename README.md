#### Install
sudo apt install python3-pip \
sudo apt install python3-venv

#### Upgrade pip and install virtualenv
python3 -m pip install --user --upgrade pip \
python3 -m pip install --user virtualenv

#### Make virtualenv named env
python3 -m venv env

#### Activate the environment env
source env/bin/activate

#### Then install this library 
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

#### Run scripts
python3 foo.py

#### Cron commands
crontab -e
###### 0 * * * * cd /home/kris/gmail; env/bin/python gmail_cleaner.py >> cron.log 2>&1
###### 0 0 * * * cd /home/kris/gmail; env/bin/python gmail_filters.py >> cron.log 2>&1
sudo tail -f /var/log/syslog \
sudo tail -f /var/log/cron.log \
sudo nano /etc/rsyslog.d/50-default.conf \
sudo systemctl restart rsyslog \ 
sudo systemctl restart cron

