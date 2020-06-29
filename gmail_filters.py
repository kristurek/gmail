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

log = log4py.setup("filters.log")


def main():
    log.debug("Started")

    credentials = gmail_commons.auth()
    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    gFilters = service.users().settings().filters().list(userId="me").execute()

    log.debug("Found: %s filters", len(gFilters["filter"]))

    emails = prepareSetOfEmails(gFilters)
    log.debug("Found: %s emails", len(emails))
    log.debug(emails)
    log.debug("Begin delete old filters")
    for gFilter in gFilters["filter"]:
        try:
            service.users().settings().filters().delete(userId="me", id=gFilter["id"]).execute()
        except errors.HttpError:
            log.error("Exception occurred on delete filters", exc_info=True)
    log.debug("End delete old filters")

    log.debug("Begin create new filters")
    emails = list(emails)  # for slicing we must convert to list
    for emails in [emails[i:i + 30] for i in range(0, len(emails), 30)]:
        try:
            message = {
                "criteria": {
                    "from": " OR ".join(emails)
                },
                "action": {
                    "addLabelIds": ["TRASH"]
                }
            }
            service.users().settings().filters().create(userId="me", body=message).execute()
            log.debug("Filter created")

        except errors.HttpError:
            log.error("Exception occurred on create filters", exc_info=True)
    log.debug("End create new filters")

    log.debug("Finished")


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
    main()
