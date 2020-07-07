FROM python:3.8-alpine

COPY gmail.py /usr/bin/gmail/
COPY main.py /usr/bin/gmail/
COPY log4py.py /usr/bin/gmail/
COPY credentials.json /usr/bin/gmail/
COPY token.pickle /usr/bin/gmail/

WORKDIR /usr/bin/gmail/

RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

ENTRYPOINT [ "python3" ]

CMD [ "main.py" ]
