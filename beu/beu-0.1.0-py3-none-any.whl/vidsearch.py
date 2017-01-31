import os
import datetime
import re
from redis_helper import REDIS
from pprint import pprint
from glob import glob
from os import remove
from kenjyco.core.input import make_selections
from kenjyco.misc.serp import youtube
from kenjyco.misc.download import av_from_link
from kenjyco.misc.vlc import play_many
from kenjyco.misc.misc import utc_now_stamp


rx_split = re.compile(r'\r?\n')


class Vidsearch(object):
    """Provides `search` and `download_next` methods
    """
    @classmethod
    def search(cls, query=None):
        if not query:
            try:
                query = input('query: ')
            except EOFError:
                return
        if not query:
            return

        timestamp_query = utc_now_stamp()
        results = youtube.search(query)
        selected = make_selections(
            results,
            wrap=False,
            item_format='{duration} .::. {title} .::. {user} .::. {uploaded}'
        )

        for item in selected:
            item.update({
                'query': query,
                'timestamp_query': timestamp_query,
            })
        if selected:
            REDIS.lpush('vids:to_download:1', selected[0])
            chunk2 = selected[1:3]
            chunk3 = selected[3:]
            if chunk2:
                REDIS.lpush('vids:to_download:2', *chunk2)
            if chunk3:
                REDIS.lpush('vids:to_download:3', *chunk3)

    @classmethod
    def show_download_queue(cls):
        for key in sorted(REDIS.scan_iter('vids:to_download:*')):
            for item in reversed(REDIS.lrange(key, 0, -1)):
                print(' - {query} .::. {title}'.format(**eval(item)))


def get_mp3_file(vid_id, path='.'):
    try:
        return glob(os.path.join(path, '*{}*.mp3'.format(vid_id)))[0]
    except IndexError:
        return ''


def get_vid_file(vid_id, path='.'):
    results = []
    for ext in ('mp4', 'flv', 'webm', 'mkv', 'mov'):
        results.extend(glob(os.path.join(path, '*{}*.{}'.format(vid_id, ext))))

    try:
        return results[0]
    except IndexError:
        return ''


def get_extra_files(vid_id, path='.', delete=False):
    try:
        files = glob(os.path.join(path, '*{}.f???.*'.format(vid_id)))
    except IndexError:
        files = []

    if delete:
        for fname in files:
            remove(fname)

    return files


def get_playlist_lines(m3u):
    try:
        with open(m3u, 'r') as fp:
            text = fp.read()
    except FileNotFoundError:
        return []

    return rx_split.split(text)


def delete_all_extra_files(path='.'):
    for fname in glob(os.path.join(path, '*.f???.*')):
        remove(fname)
        print('Removed {}'.format(repr(fname)))
    for fname in glob(os.path.join(path, '**/*.f???.*')):
        remove(fname)
        print('removed {}'.format(repr(fname)))


if __name__ == '__main__':
    import sys
    import re
    import time

    try:
        query = sys.argv[1]
    except IndexError:
        query = input('What is your query: ')

    results = youtube.search(query)

    selected = make_selections(
        results,
        wrap=False,
        item_format='{duration} .::. {title} .::. {user} .::. {uploaded}',
    )

    if selected:
        if not os.path.exists(query):
            os.makedirs(query)
        os.chdir(query)

        pprint(selected)

        links = [x['link'] for x in selected]
        with open('links.txt', 'a') as fp:
            fp.write('\n'.join(links))

        with open('selected--{}.dict'.format(int(time.time())), 'w') as fp:
            pprint(selected, fp)

        mp3s = []
        vids = []
        path = os.getcwd()
        playlist_lines = get_playlist_lines('vids.m3u')

        for item in selected:
            link = item['link']
            print('\nDownloading {} ...'.format(link))
            result = av_from_link(link, playlist=True, quiet=False, audio_only=False, mp3=False)
            if not result:
                continue

            get_extra_files(result['id'], path, delete=True)

            mp3 = get_mp3_file(result['id'], path)
            vid = get_vid_file(result['id'], path)
            if mp3:
                mp3s.append(mp3)
            with open('mp3s.txt', 'a') as fp:
                fp.write('{}\n'.format(mp3))
            if vid != ''  and vid not in playlist_lines:
                vids.append(vid)
                with open('vids.m3u', 'a') as fp:
                    fp.write('{}\n'.format(vid))

            # pprint(result)

            # try:
            #     hash_id = redis_helper.next_object_id('misc:downloaded:vid')
            #     redis_helper.add_dict(hash_id, item, indexfields=['_id', 'query'], prefix='misc', use_time=True)
            # except:
            #     pass

        print('\nFiles saved to {}'.format(repr(path)))

        response = input('Do you want to watch now? (y/n): ')
        if response.lower().startswith('y'):
            play_many(*vids)
