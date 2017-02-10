from django.contrib.staticfiles.storage import staticfiles_storage
def get_js():
    return staticfiles_storage.url('submenu/bootstrap-submenu.js')
def get_css():
    return staticfiles_storage.url('submenu/bootstrap-submenu.min.css')
def get_examples():
    return 'https://vsn4ik.github.io/bootstrap-submenu/#html-examples'
