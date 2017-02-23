from amaascore.books.book import Book


def json_to_book(json_book):
    book = Book(**json_book)
    return book
