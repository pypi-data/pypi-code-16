# coding=utf-8


def reread_registry(context):
    ''' Reread the registry to initialize the
    experimental.bwtools.known_bad_ips record
    '''
    context.runImportStepFromProfile(
        'profile-experimental.bwtools:default',
        'plone.app.registry',
    )
