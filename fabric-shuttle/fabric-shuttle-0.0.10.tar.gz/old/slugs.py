from random import randint

from django.template.defaultfilters import slugify

# instance must have a field named slug for this method to work
def unique_slug_generator(instance, text, suffix_length=9, max_length=50):
	text = slugify(text)[:max_length - suffix_length]
	num = str(randint(10 ** (suffix_length - 1), (10 ** suffix_length) - 1))
	potential_slugs = [text + '-'[:x] + num[:x] for x in range(suffix_length + 1)]
	taken_slugs = list(instance.__class__.objects.filter(slug__in=potential_slugs).values_list('slug', flat=True))
	for slug in potential_slugs:
		try:
			taken_slugs.index(slug)
		except:
			yield slug
