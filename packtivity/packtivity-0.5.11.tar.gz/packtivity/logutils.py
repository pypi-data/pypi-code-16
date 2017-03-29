import os
import logging
from packtivity.utils import mkdir_p

def setup_logging(context, nametag):
    ## prepare logging for the execution of the job. We're ready to handle up to DEBUG
    log = logging.getLogger('step_logger_{}'.format(nametag))
    log.setLevel(logging.DEBUG)

    print 'LUKE...',log.handlers, os.getpid()

    ## this is all internal loggin, we don't want to escalate to handlers of parent loggers
    ## we will have two handlers, a stream handler logging to stdout at INFO
    log.propagate = False
    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    fh  = logging.StreamHandler()
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    log.addHandler(fh)

    # short interruption to create metainfo storage location
    metadir  = '{}/_packtivity'.format(context['readwrite'][0])
    context['metadir'] = metadir

    log.info('creating metadirectory %s if necessary. exists? : %s',metadir,os.path.exists(metadir))
    utils.mkdir_p(metadir)

    # Now that we have  place to store meta information we put a file based logger in place
    # to log at DEBUG
    logname = '{}/{}.step.log'.format(metadir,nametag)
    fh  = logging.FileHandler(logname)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    log.addHandler(fh)
