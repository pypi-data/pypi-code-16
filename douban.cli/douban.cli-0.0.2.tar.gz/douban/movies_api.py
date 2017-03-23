import requests

class MoviesAPI:

    def __init__(self):
        self.base_url = 'https://api.douban.com/v2/movie/'

    # dic_obj = {'q':'movie_name', 'tag': 'movie_tag', 'start': offset, 'count': 100}
    def search_movie(self, query_dic):
        url = self.base_url + 'search'
        movies = self.get(url=url, query=query_dic)
        return movies

    def get(self, url, query={}):
        return requests.get(url, params=query).json()
