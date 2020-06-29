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

from __future__ import print_function

from apiclient import errors
from googleapiclient.discovery import build

import gmail_commons
import log4py

log = log4py.setup("cleaner.log")


def main():
    log.debug("Started")

    credentials = gmail_commons.auth()
    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    results = service.users().settings().filters().list(userId="me").execute()

    log.debug("Found: %s filters", len(results["filter"]))

    messages = []

    for obj in results["filter"]:
        query = "from:(" + obj["criteria"]["from"] + ")"
        log.debug("Query [%s]", query)

        try:
            # Search in SPAM
            response = service.users().messages().list(userId="me", q=query, includeSpamTrash=True,
                                                       labelIds=["SPAM"]).execute()
            if "messages" in response:
                messages.extend(response["messages"])
                log.debug("Found: %s messages for current query in SPAM", len(response["messages"]))

            while "nextPageToken" in response:
                page_token = response["nextPageToken"]
                response = service.users().messages().list(userId="me", q=query, includeSpamTrash=True,
                                                           labelIds=["SPAM"],
                                                           pageToken=page_token).execute()
                messages.extend(response["messages"])
                log.debug("Found: %s messages for current query in SPAM", len(response["messages"]))

            # Search in TRASH
            response = service.users().messages().list(userId="me", q=query, includeSpamTrash=True,
                                                       labelIds=["TRASH"]).execute()
            if "messages" in response:
                messages.extend(response["messages"])
                log.debug("Found: %s messages for current query in TRASH", len(response["messages"]))

            while "nextPageToken" in response:
                page_token = response["nextPageToken"]
                response = service.users().messages().list(userId="me", q=query, includeSpamTrash=True,
                                                           labelIds=["TRASH"],
                                                           pageToken=page_token).execute()
                messages.extend(response["messages"])
                log.debug("Found: %s messages for current query in TRASH", len(response["messages"]))

        except errors.HttpError:
            log.error("Exception occurred on execution query", exc_info=True)

    ids = [message["id"] for message in messages]
    log.debug("Total message to delete: %s", len(ids))

    if ids:
        try:
            # ---------------
            ids = ids[0:1]
            if len(ids) > 1:  # TODO only for tests
                raise Exception("Too many IDS")
            # ---------------
            message = {"ids": ids}
            service.users().messages().batchDelete(userId="me", body=message).execute()
            log.debug("Messages deleted")

        except errors.HttpError:
            log.error("Exception occurred on delete", exc_info=True)

    log.debug("Finished")


if __name__ == "__main__":
    main()