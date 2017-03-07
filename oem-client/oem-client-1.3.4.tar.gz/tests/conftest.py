# from oem.media.movie import MovieMatch
# from oem.media.show import EpisodeMatch
#
#
# def pytest_assertrepr_compare(op, left, right):
#     if op == "==" and (isinstance(left, EpisodeMatch) or isinstance(right, EpisodeMatch)):
#         return [
#             '%r == %r' % (left, right)
#         ]
#
#     if op == "==" and (isinstance(left, MovieMatch) or isinstance(right, MovieMatch)):
#         return [
#             '%r == %r' % (left, right)
#         ]
