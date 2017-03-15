from fanstatic import Group, Library, Resource
import js.angular

library = Library('angular-xeditable', 'resources')

angular_xeditable_css = Resource(
    library, 'css/xeditable.css',
    minified='css/xeditable.min.css')

angular_xeditable_js = Resource(
    library, 'js/xeditable.js',
    minified='js/xeditable.min.js',
    depends=[js.angular.angular])

angular_xeditable = Group([angular_xeditable_js, angular_xeditable_css])
