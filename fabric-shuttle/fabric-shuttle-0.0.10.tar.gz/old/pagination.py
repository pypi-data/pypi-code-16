
# Works on 0-based index, with 1-based index text
def pagination_pages(current_page, total_pages, pagination_size=5, space_text='...', prev_text='<', next_text='>'):
	class PaginationPage:
		def __init__(self, enabled, text, number=1):
			self.enabled = enabled
			self.text = text
			self.number = number
	pages = []
	pagination_size /= 2
	lower = current_page - pagination_size
	upper = current_page + pagination_size
	if lower < 0:
		upper += -lower
		lower = 0
	if upper >= total_pages:
		upper = total_pages - 1
	# Back button
	pages.append(PaginationPage(True if current_page > 0 else False, prev_text, current_page - 1))
	# Spacer
	if lower > 0:
		pages.append(PaginationPage(False, space_text))
	# Number buttons
	for x in xrange(lower, upper + 1):
		pages.append(PaginationPage(False if x == current_page else True, str(x + 1), x))
	# Spacer
	if upper < (total_pages - 1):
		pages.append(PaginationPage(False, space_text))
	# Next button
	pages.append(PaginationPage(True if current_page < (total_pages - 1) else False, next_text, current_page + 1))
	return pages
