FROM python:3.8-alpine

COPY gmail.py /
COPY main.py /
COPY log4py.py /
COPY credentials.json /
COPY token.pickle /
COPY emails.json /

WORKDIR /

RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

ENTRYPOINT [ "python3" ]

CMD [ "main.py" ]
