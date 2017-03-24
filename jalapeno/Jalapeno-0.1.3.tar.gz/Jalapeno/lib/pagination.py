import math
class Pagination(object):
	
	def __init__(self,page,per_page,iterable):
		self.page = page
		self.per_page = per_page
		self.iterable = iterable
		self.total = len(iterable)
		
	@property
	def total_pages(self):
		return int(math.ceil(len(self.iterable)/self.per_page))
		
	@property
	def has_prev(self):
		return self.page > 1
	
	@property
	def has_next(self):
		return self.page < self.total_pages
	
	@property
	def pager(self):
		return list(range(1,self.total_pages+1))
	
	@property
	def items(self):
		index = self.page - 1
		start = index * self.per_page
		end = start + self.per_page
		
		return self.iterable[start:end]
		
		
#源代码作者Beluki
#https://github.com/Beluki/Frozen-Blog/blob/master/Source/blog.py