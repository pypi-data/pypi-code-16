import json
from entity import Entity

class Episode(Entity):

  def __init__(self, series, entry):
    """Constructor"""

    # Fill fields
    self.type         = 'episode'
    self.seriesId     = series.id
    self.seriesTitle  = series.title # Already encoded
    self.imageUrlSm   = series.imageUrlSm # Already encoded
    self.imageUrlLg   = series.imageUrlLg # Already encoded
    self.title        = '' if 'title' not in entry else entry['title'].encode('utf-8')
    self.author       = '' if 'author' not in entry else entry['author'].encode('utf-8')
    self.summary      = '' if 'summary_detail' not in entry else entry['summary_detail']['value'].encode('utf-8')
    self.pubDate      = '' if 'published_parsed' not in entry else self._build_date_str(entry['published_parsed'])
    self.duration     = '' if 'itunes_duration' not in entry else entry['itunes_duration'].encode('utf-8')
    self.tags         = [] if 'tags' not in entry else [(t['term'] if t['term'] is None else t['term'].encode('utf-8')) for t in entry['tags']]

    # Grab audio_url
    self.audioUrl = None
    if 'links' in entry:
      for l in entry['links']:
        if ('type' in l) and ('href' in l) and ('type' in l) and ('audio' in l['type']):
          self.audioUrl = l['href'].encode('utf-8'); break
