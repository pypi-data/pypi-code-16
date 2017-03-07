import json
from entity import Entity

class Series(Entity):

  # Static (class variable, access via
  # Series.fields)
  fields = ['id', 'title', 'country', 'author', 'imageUrlSm',
            'imageUrlLg', 'feedUrl', 'genres']


  def __init__(self, s_id, title, country, author, image_url_sm, image_url_lg, feed_url, genres):
    """
    Constructor -
    NOTE: `genres` is ';'-delimitted list of genres as a string
    """
    self.type         = 'series'
    self.id           = s_id
    self.title        = title.encode('utf-8')
    self.country      = country.encode('utf-8')
    self.author       = author.encode('utf-8')
    self.imageUrlSm   = image_url_sm.encode('utf-8')
    self.imageUrlLg   = image_url_lg.encode('utf-8')
    self.feedUrl      = feed_url.encode('utf-8')
    self.genres       = genres.encode('utf-8')


  def __hash__(self):
    """Series ID defines uniqueness"""
    return self.id


  @classmethod
  def from_json(cls, J):
    """Series from iTunes JSON `J`"""
    return cls(J['collectionId'], J['collectionName'], J['country'],
               J['artistName'], J['artworkUrl60'], J['artworkUrl600'],
               J['feedUrl'], ';'.join(J['genres']))


  @classmethod
  def from_line(cls, L):
    """Series from CSV line `L`"""
    return cls(int(L['id'].decode('utf-8')), L['title'].decode('utf-8'),
                   L['country'].decode('utf-8'), L['author'].decode('utf-8'),
                   L['imageUrlSm'].decode('utf-8'), L['imageUrlLg'].decode('utf-8'),
                   L['feedUrl'].decode('utf-8'), L['genres'].decode('utf-8'))


  def to_line(self):
    """To 'line' (a.k.a. array we can write with csv module)"""
    my_dict = self.__dict__
    return [my_dict[f] for f in Series.fields]
