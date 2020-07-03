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

#### Cron
crontab -e
###### */1 * * * * cd /home/kris/gmail; env/bin/python gmail.py >> cron.log 2>&1

#### DOCKER
docker buildx build -t ${DOCKER_USER}/gmail:0.0.1 --platform linux/amd64,linux/arm64 . --push \
docker run -d --restart always ${DOCKER_USER}/gmail:0.0.1 \
docker inspect 47324d41f24e \
docker cp 47324d41f24e:/gmail.log . \

https://medium.com/@artur.klauser/building-multi-architecture-docker-images-with-buildx-27d80f7e2408 \