# -*- coding: utf-8 -*-

import pymysql.cursors
import os


def check_consistency(user, password, host, database):
    conn = pymysql.connect(user=user, password=password,
                           host=host, database=database)

    try:
        with conn.cursor() as cur:
            sql = "SELECT id from articles_articles;"
            cur.execute(sql)
            ids = [r[0] for r in cur.fetchall()]
            for id in ids:
                if not os.path.exists("/var/pti/scrape/{}.txt".format(id)):
                    print("Not found scraped text: id -> {}".format(id))

    finally:
        conn.close()


if __name__ == "__main__":
    user = os.environ.get('PTI_USER')
    password = os.environ.get('PTI_PASSWORD')
    host = os.environ.get('PTI_HOST')
    db = os.environ.get('PTI_DB')
    check_consistency(user, password, host, db)
