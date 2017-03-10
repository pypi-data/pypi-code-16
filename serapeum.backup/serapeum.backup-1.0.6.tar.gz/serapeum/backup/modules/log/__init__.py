import logging
from os.path import isdir
from os import mkdir

if not isdir('/var/log/serapeum'):
    mkdir('/var/log/serapeum', mode=0o755)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename='/var/log/serapeum/run.log',
    filemode='w'
)

logger = logging.getLogger('serapeum-backup')
