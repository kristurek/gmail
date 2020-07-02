# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
import pickle

from apiclient import errors
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import log4py

log = log4py.setup("gmail.log", logging.INFO)


def main():
    log.info("Started")

    credentials = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", ["https://mail.google.com/",
                                                                                  "https://www.googleapis.com/auth/gmail.settings.basic"])
            credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    gService = build("gmail", "v1", credentials=credentials, cache_discovery=False)

    gFilters = gService.users().settings().filters().list(userId="me").execute()
    emails = prepareSetOfEmails(gFilters)

    log.info("Found: %s filters with %s addresses", len(gFilters["filter"]), len(emails))

    savedEmails = restoreSetOfEmails("emails.json")

    if emails != savedEmails:
        storeSetOfEmails("emails.json", emails)

        log.info("Recreate filters")

        log.debug("Begin delete old filters")
        for gFilter in gFilters["filter"]:
            gService.users().settings().filters().delete(userId="me", id=gFilter["id"]).execute()
        log.debug("End delete old filters")

        log.debug("Begin create new filters")
        emails = list(emails)  # for slicing we must convert to list
        for emails in [emails[i:i + 30] for i in range(0, len(emails), 30)]:
            message = {
                "criteria": {
                    "from": " OR ".join(emails)
                },
                "action": {
                    "addLabelIds": ["TRASH"]
                }
            }
            gService.users().settings().filters().create(userId="me", body=message).execute()
            log.debug("Filter created")
    else:
        log.info("Filters not changed")

    messages = []

    for obj in gFilters["filter"]:
        query = "from:(" + obj["criteria"]["from"] + ")"
        log.debug("Query [%s]", query)

        messages.extend(searchMessages(gService, query, "SPAM"))
        messages.extend(searchMessages(gService, query, "TRASH"))

    ids = [message["id"] for message in messages]
    log.info("Founded %s messages to delete", len(ids))

    if ids:
        message = {"ids": ids}
        gService.users().messages().batchDelete(userId="me", body=message).execute()
        log.debug("Messages deleted")

    log.info("Finished")


def searchMessages(gService, query, label):
    messages = []
    response = gService.users().messages().list(userId="me", q=query, includeSpamTrash=True,
                                                labelIds=[label]).execute()
    if "messages" in response:
        messages.extend(response["messages"])

    while "nextPageToken" in response:
        page_token = response["nextPageToken"]
        response = gService.users().messages().list(userId="me", q=query, includeSpamTrash=True,
                                                    labelIds=[label],
                                                    pageToken=page_token).execute()
        messages.extend(response["messages"])

    log.debug("Found: %s messages for current query in %s", len(messages), label)

    return messages


def restoreSetOfEmails(fileName: str):
    log.info("Restore %s file", fileName)

    emails = []
    if os.path.exists(fileName):
        with open(fileName, 'r') as fileHandle:
            emails = json.load(fileHandle)
            log.info("Found %s addresses in file", len(emails))
    else:
        log.info("File doesn't exists")

    return set(emails)


def storeSetOfEmails(fileName: str, emails: set):
    log.info("Store emails to %s file", fileName)
    log.debug(emails)

    with open(fileName, 'w') as fileHandle:
        json.dump(list(emails), fileHandle)


def prepareSetOfEmails(filters: dict) -> set:
    emails = set()

    for gFilter in filters["filter"]:
        gFrom = gFilter["criteria"]["from"]
        gFrom = gFrom.replace("(", "")
        gFrom = gFrom.replace(")", "")

        sEmails = [email.strip() for email in gFrom.split("OR")]
        emails = emails | set(sEmails)

    # save full gmail emails
    exclusions = set(filter(lambda x: "gmail.com" in x and x != "@gmail.com", emails))

    # remove gmail emails from set
    emails = set(filter(lambda x: "gmail.com" not in x, emails))

    # convert from foo@email.com to @email.com
    emails = set([x[x.index("@"):len(x)] for x in emails])

    # add to set saved gmail emails
    emails |= exclusions

    return emails


if __name__ == "__main__":
    try:
        main()
    except errors.HttpError:
        log.error("Exception occurred on execution gmail.py", exc_info=True)
