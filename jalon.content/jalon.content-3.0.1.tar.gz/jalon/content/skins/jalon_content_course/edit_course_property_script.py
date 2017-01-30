## Controller Python Script "edit_course_property_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

form = context.REQUEST.form

course_property = form["course_property"]
context.setCourseProperties({course_property.capitalize(): form[course_property]})
context.setCourseProperties({"DateDerniereModif" : DateTime()})

if course_property in ["acces", "description", "activer_email_forum", "add_forum_permission"]:
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.absolute_url()
