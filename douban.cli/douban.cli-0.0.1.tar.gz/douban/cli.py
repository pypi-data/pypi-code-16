import sys
import fire
from douban.books_api import BooksAPI
from douban.movies_api import MoviesAPI

class DouBanCLI(object):

    def book(self, *book_name_strings):
        api = BooksAPI()
        book_name = ' '.join(book_name_strings)
        res = api.search_book({'q': book_name, 'count': 1})
        book = self._get_first_matched_id_from(res, 'book')
        self._print_book_info(book)

    def movie(self, *movie_name_strings):
        api = MoviesAPI()
        movie_name = ' '.join(movie_name_strings)
        res = api.search_movie({'q': movie_name, 'count': 1})
        movie = self._get_first_matched_id_from(res, 'movie')
        self._print_movie_info(movie)

    def _get_first_matched_id_from(self, res, obj_type='book'):
        print('共%s个结果，返回第1个结果' %res['total'])
        mapper = {'book': 'books', 'movie': 'subjects'}
        key = mapper[obj_type]
        return res[key][0]

    def _print_book_info(self, book):
        if book != None:
            # print(book)
            print()
            print('书名: %s' % book['title'])
            print()
            print('作者: %s' % ' '.join(book['author']))
            print('作者简介: %s' % book['author_intro'])
            print()
            print('页数: %s' % book['pages'])
            print('出版日期: %s' % book['pubdate'])
            print('定价: %s' % book['price'])
            self._print_rating(book['rating'])
            self._print_tags(book['tags'])
            print()
            print('简介: %s' % book['summary'])
            # print()
            # print('目录: %s' % book['catalog'])
        else:
            print('无法找到相关结果')

    def _print_rating(self, rating, obj_type='book'):
        if obj_type == 'book':
            print('共有%s人次评分, 平均分: %s'%(rating['numRaters'], rating['average']))
        else:
            print('共有%s人收藏, 平均分: %s'%(rating['stars'], rating['average']))

    def _print_tags(self, tags):
        tag_names = [tag['name'] for tag in tags]
        print('标签: %s' % ', '.join(tag_names))

    def _print_movie_info(self, movie):
        if movie != None:
            print('名称: %s' % movie['title'])
            self._print_rating(movie['rating'], 'movie')
            print('年份: %s' % movie['year'])
            print('类型: %s' % movie['subtype'])
            print('导演: %s' % self._get_name(movie['directors']))
            print('主演: %s' % self._get_name(movie['casts']))
            print('分类: %s' % ' '.join(movie['genres']))
        else:
            print('无法找到相关结果')

    def _get_name(self, directors_or_actors):
        return ', '.join([someone['name'] for someone in directors_or_actors])

def main():
    cli = DouBanCLI()
    fire.Fire(cli)

if __name__ == '__main__':
    main()
