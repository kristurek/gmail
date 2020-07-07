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
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def main():
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

    emails = restoreSetOfEmails("emails.json")

    for gFilter in gFilters["filter"]:
        gService.users().settings().filters().delete(userId="me", id=gFilter["id"]).execute()

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


def restoreSetOfEmails(fileName: str):
    emails = []
    if os.path.exists(fileName):
        with open(fileName, 'r') as fileHandle:
            emails = json.load(fileHandle)

    return set(emails)


if __name__ == "__main__":
    main()
