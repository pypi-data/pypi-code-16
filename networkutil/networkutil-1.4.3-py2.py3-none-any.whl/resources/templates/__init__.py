import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

jumpbox = u'{base}{filename}'.format(base=base_dir, filename=u'jumpbox.json')
