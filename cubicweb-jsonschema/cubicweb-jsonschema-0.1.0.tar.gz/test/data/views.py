from cubicweb.web.views import uicfg


afs = uicfg.autoform_section
pvs = uicfg.primaryview_section

afs.tag_attribute(('CWUser', 'lastname'), 'main', 'hidden')
afs.tag_attribute(('CWUser', 'surname'), 'main', 'hidden')
pvs.tag_subject_of(('CWUser', 'use_email', 'EmailAlias'), 'hidden')
pvs.tag_attribute(('CWUser', 'login'), 'hidden')
afs.tag_object_of(('*', 'use_email', 'EmailAlias'), 'main', 'hidden')
afs.tag_subject_of(('CWUser', 'picture', '*'), 'main', 'inlined')
afs.tag_subject_of(('Photo', 'thumbnail', '*'), 'main', 'inlined')

# we don't want this to interfere with entity creation/edition tests 
afs.tag_subject_of(('CWUser', 'use_email', 'EmailAlias'), 'main', 'hidden')
