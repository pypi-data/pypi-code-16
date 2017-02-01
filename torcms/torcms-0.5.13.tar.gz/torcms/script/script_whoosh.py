# -*- coding: UTF-8 -*-

import os
import html2text
import tornado.escape

from whoosh.index import create_in, open_dir
from whoosh.fields import *

from jieba.analyse import ChineseAnalyzer

from torcms.model.post_model import MPost
from torcms.model.info_model import MInfor as MApp

from torcms.model.category_model import MCategory as  MInforCatalog
from torcms.model.post2catalog_model import MPost2Catalog
# from torcms.model.infor2catalog_model import MInfor2Catalog

from torcms.model.wiki_model import MWiki
# from torcms.model.page_model import MPage

from config import router_post

mappcat = MInforCatalog()
minfo2tag = MPost2Catalog()


def do_for_app(writer, rand=True, kind='', doc_type={}):
    mpost = MApp()
    if rand:
        recs = mpost.query_random(50, kind=kind)
    else:
        recs = mpost.query_recent(50, kind=kind)

    for rec in recs:
        text2 = rec.title + ',' + html2text.html2text(tornado.escape.xhtml_unescape(rec.cnt_html))
        writer.update_document(
            catid='00000',
            title=rec.title,
            type=doc_type[rec.kind],
            link='/{0}/{1}'.format(router_post[rec.kind], rec.uid),
            content=text2
        )


def do_for_app2(writer, rand=True):
    mpost = MApp()
    if rand:
        recs = mpost.query_random(50)
    else:
        recs = mpost.query_recent(50)

    for rec in recs:
        text2 = rec.title + ',' + html2text.html2text(tornado.escape.xhtml_unescape(rec.cnt_html))

        info = minfo2tag.get_entry_catalog(rec.uid)
        if info:
            pass
        else:
            continue

        catid = info.tag.uid[:2] + '00'

        cat_name = ''
        if 'def_cat_uid' in rec.extinfo and rec.extinfo['def_cat_uid']:
            uu = mappcat.get_by_uid(rec.extinfo['def_cat_uid'][:2] + '00')
            if uu:
                cat_name = uu.name
        writer.update_document(
            title=rec.title,
            catid=catid,
            type='<span style="color:red;">[{0}]</span>'.format(cat_name),
            link='/{0}/{1}'.format(router_post[rec.kind], rec.uid),
            content=text2
        )


def do_for_post(writer, rand=True, doc_type=''):
    mpost = MPost()
    if rand:
        recs = mpost.query_random(50)
    else:
        recs = mpost.query_recent(50)

    for rec in recs:
        text2 = rec.title + ',' + html2text.html2text(tornado.escape.xhtml_unescape(rec.cnt_html))
        writer.update_document(
            title=rec.title,
            catid='0000',
            type=doc_type,
            link='/post/{0}'.format(rec.uid),
            content=text2
        )


def do_for_wiki(writer, rand=True, doc_type=''):
    mpost = MWiki()
    if rand:
        recs = mpost.query_random(50, )
    else:
        recs = mpost.query_recent(50, )

    for rec in recs:
        text2 = rec.title + ',' + html2text.html2text(tornado.escape.xhtml_unescape(rec.cnt_html))
        writer.update_document(
            title=rec.title,
            catid='0000',
            type=doc_type,
            link='/wiki/{0}'.format(rec.title),
            content=text2
        )


def do_for_page(writer, rand=True, doc_type=''):
    mpost = MWiki()
    if rand:
        recs = mpost.query_random(50, )
    else:
        recs = mpost.query_recent(50, )

    for rec in recs:
        text2 = rec.title + ',' + html2text.html2text(tornado.escape.xhtml_unescape(rec.cnt_html))
        writer.update_document(
            title=rec.title,
            catid='0000',
            type=doc_type,
            link='/page/{0}'.format(rec.uid),
            content=text2
        )


def gen_whoosh_database(if_rand=True, kind='1', kind_arr=[], post_type={}):
    analyzer = ChineseAnalyzer()
    schema = Schema(title=TEXT(stored=True, analyzer=analyzer),
                    catid=TEXT(stored=True),
                    type=TEXT(stored=True),
                    link=ID(unique=True, stored=True, ),
                    content=TEXT(stored=True, analyzer=analyzer))
    whoosh_db = 'database/whoosh'
    if not os.path.exists(whoosh_db):
        os.makedirs(whoosh_db)
        ix = create_in(whoosh_db, schema)
    else:
        ix = open_dir(whoosh_db)

    writer = ix.writer()

    do_for_app2(writer, rand=if_rand)

    do_for_post(writer, rand=if_rand, doc_type=post_type['1'])
    do_for_wiki(writer, rand=if_rand, doc_type=post_type['1'])
    do_for_page(writer, rand=if_rand, doc_type=post_type['1'])

    for kind in kind_arr:
        do_for_app(writer, rand=if_rand, kind=kind, doc_type=post_type)
    writer.commit()
