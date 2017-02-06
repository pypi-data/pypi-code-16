#!/usr/bin/python
# -*- coding: utf8 -*-

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

import sys
import logging
from clize import run
from os.path import basename, splitext
import csv
from collections import deque
from .geofluent import GeoFluent


def translate(key, secret, source, target, content):
    """
    Translates the content from the source to the target language,
    exporting the result to a CSV in the working directory.

    key: geofluent api key

    secret: geofluent api secret (encoded in base64)

    source: source language

    target: target language

    content: file with content to translate per line

    """

    logging.basicConfig(level=logging.DEBUG, format="\033[1m%(name)s\033[0m %(message)s")
    logging.getLogger("requests").setLevel(logging.WARNING)
    log = logging.getLogger("geofluent")

    gf = GeoFluent(key=key, secret=secret)
    log.info("Initialized GeoFluent Python Client with JWT token %s", gf.token)

    languages = [(i["source"]["code"], i["target"]["code"]) for i in gf.languages()]
    log.debug("Languages supported: %s", ", ".join(["%s->%s" % language for language in languages]))
    if (source, target) not in languages:
        log.error("Current profile doesn't provide support for translating from '%s' to '%s'; exiting...", source, target)
        sys.exit(-1)

    translations = []
    length = 0
    last_messages = deque([], 10)

    try:
        with open(content, "r") as f:
            for line in f:
                line = line.rstrip('\n')
                if len(line) == 0:
                    log.debug("Skipped empty line")
                elif line in last_messages:
                    log.debug("Skipped duplicated line: %s", line)
                else:
                    log.debug("Translating '%s'...", line)
                    while True:
                        try:
                            translation = gf.translate(line, source, target)
                            translations.append((line, translation))
                            last_messages.append(line)
                            length += 1
                            if length % 100 == 0:
                                log.info("%d translations done", length)
                        except ConnectionResetError as e:
                            log.error("%s translating '%s': %s", type(e).__name__, line, str(e))
                            log.debug("Retrying...")
                            continue
                        except RuntimeError as e:
                            log.error("Error translating '%s': %s", line, str(e))
                        break
    except KeyboardInterrupt:
        log.info("Forced exiting...")

    csv_path = "%s.csv" % splitext(basename(content))[0]
    with open(csv_path, "w", encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([source, target])
        for translation in translations:
            writer.writerow(translation)

    log.info("Exported %d translations to %s", len(translations), csv_path)


def main():
    run(translate)


if __name__ == "__main__":
    main()

