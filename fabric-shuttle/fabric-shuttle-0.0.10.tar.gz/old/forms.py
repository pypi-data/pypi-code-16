
def add_widget_attrs(form, filter=None, **attrs):
	"""Add attributes to all widgets in a form before rendering. Sometimes easier than specifying in the form."""
	for attr in attrs:
		for field in form.fields.values():
			if filter and not filter(field):
				continue
			if field.widget.attrs.has_key(attr):
				field.widget.attrs[attr] = '%s %s' % (field.widget.attrs[attr], attrs[attr])
			else:
				field.widget.attrs[attr] = attrs[attr]
