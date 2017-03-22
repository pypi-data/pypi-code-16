import requests

class BooksAPI:

    def __init__(self):
        self.base_url = 'https://api.douban.com/v2/book/'

    def get_book_info(self, book_id):
        url = self.base_url + str(book_id)
        book = self.get(url=url)
        return book

    def get_book_info_from_isbn(self, isbn):
        url = self.base_url + 'isbn/' + str(isbn)
        book = self.get(url=url)
        return book

    # dic_obj = {'q':'book_name', 'tag': 'book_tag', 'start': offset, 'count': 100}
    def search_book(self, query_dic):
        url = self.base_url + 'search'
        books = self.get(url=url, query=query_dic)
        return books

    def get(self, url, query={}):
        return requests.get(url, params=query).json()
