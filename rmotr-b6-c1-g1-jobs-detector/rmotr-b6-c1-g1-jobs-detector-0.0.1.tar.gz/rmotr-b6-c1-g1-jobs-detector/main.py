import click
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from jobs_detector import settings

import logging, sys
logging.basicConfig(filename=settings.LOG, level=logging.DEBUG)
logging.info('------ START: {} -------'.format(str(datetime.now())))

DEFAULT_KEYWORDS = [
    'remote',
    'postgres',
    'python',
    'javascript',
    'react',
    'pandas',
]

@click.group()
def jobs_detector():
    pass

@jobs_detector.command()
@click.option('-i', '--post-id', type=str, required=True)
@click.option('-k', '--keywords', type=str, default=','.join(DEFAULT_KEYWORDS),
              callback=lambda _, x: x.split(',') if x else x)
@click.option('-c', '--combinations', type=str, default=None,
              callback=lambda _, x: x.split(',') if x else x)
              
def hacker_news(post_id, keywords, combinations):
    """
    This subcommand aims to get jobs statistics by parsing "who is hiring?"
    HackerNews posts based on given set of keywords.
    """
    logging.info('hacker_news -i {} -k {} -c {}'.format( post_id, keywords, combinations))
    
    # Set up dictionaries with counters
    k_counter = {}
    for keyword in keywords:
        k_counter[keyword] = 0
        
    if combinations:
        c_counter = {}
        for combo in combinations:
            c_counter[combo] = 0
    
    url = settings.BASE_URL.format(post_id)

    try:
        html = requests.get(url).content
    except:
        logging.warning("Could not connect to {}".format(url))
        
    soup = BeautifulSoup(html, 'html.parser')
    
    posts = soup.find_all('img', width="0")
    
    for post in posts:
        
        try:
            parent = post.parent.next_sibling.next_sibling
            comment = parent.get_text()
            logging.info(type(comment))
        
            # Find keywords in text
            comment_words = comment.lower()
            
            for keyword in keywords:
                if keyword.lower() in comment_words:
                    k_counter[keyword] += 1
                  
            if combinations:
                for combination in combinations:
                    each_word = combination.lower().split('-')
                    # if all([word in comment_words for word in each_word]):
                    #         c_counter[combination] += 1
                    if each_word[0] in comment_words:
                        if each_word[1] in comment_words:
                            c_counter[combination] += 1
        except:
            logging.warning("Failed to fetch a post.")
            logging.info(post)
            continue
    
    # Std Output
    click.echo('Total job posts: {}'.format(len(posts)))

    click.echo('Keywords:')
    for keyword in keywords:
        v = k_counter[keyword]
        percent = int((float(v)/len(posts))*100)
        click.echo('{}: {} ({}%)'.format(keyword.title(), v, percent))
    
    if combinations:
        click.echo('Combinations:')
        for combination in combinations:
            v = c_counter[combination]
            percent = int((float(v)/len(posts))*100)
            click.echo('{}: {} ({}%)'.format(combination.title(), v, percent))


if __name__ == '__main__':
    jobs_detector()
