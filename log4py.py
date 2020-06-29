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

import logging.handlers
import sys
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


def setup(filename: str) -> logging.RootLogger:
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    if log.hasHandlers():
        log.handlers.clear()

    streamHandler = StreamHandler(sys.stdout)
    streamHandler.setFormatter(formatter)
    log.addHandler(streamHandler)

    fileHandler = RotatingFileHandler(filename, maxBytes=(1 * 1024 * 1024), backupCount=7)
    fileHandler.setFormatter(formatter)
    log.addHandler(fileHandler)

    return log