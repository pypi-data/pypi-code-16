import json
from entity import Entity

class Episode(Entity):

  def __init__(self, series, entry):
    """Constructor"""

    # Fill fields
    self.type         = 'episode'
    self.series_id    = series.id
    self.series_title = series.title # Already encoded
    self.image_url_sm = series.image_url_sm # Already encoded
    self.image_url_lg = series.image_url_lg # Already encoded
    self.title        = '' if 'title' not in entry else entry['title'].encode('utf-8')
    self.author       = '' if 'author' not in entry else entry['author'].encode('utf-8')
    self.summary      = '' if 'summary_detail' not in entry else entry['summary_detail']['value'].encode('utf-8')
    self.pub_date     = '' if 'published_parsed' not in entry else self._build_date_str(entry['published_parsed'])
    self.duration     = '' if 'itunes_duration' not in entry else entry['itunes_duration'].encode('utf-8')
    self.tags         = [] if 'tags' not in entry else [(t['term'] if t['term'] is None else t['term'].encode('utf-8')) for t in entry['tags']]

    # Grab audio_url
    self.audio_url = None
    if 'links' in entry:
      for l in entry['links']:
        if ('type' in l) and ('href' in l) and ('type' in l) and ('audio' in l['type']):
          self.audio_url = l['href'].encode('utf-8'); break
