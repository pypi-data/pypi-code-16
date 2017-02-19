# -*- coding: utf-8 -*-
"""
Deploy k8sdc solutions to the k8s cluster.

usage:
  k8sdc [--debug] sol [<solution>] [--help | -h]

options:
  <solution>    is a specific solution to deploy.
  -h, --help    show this help.
  --debug       show debug output.

example:
  k8sdc sol
  k8sdc sol cs1_cluster_services
"""

import logging
import os
from docopt import docopt
from k8sdc.utility import call_ansible

logger = logging.getLogger(__name__)


class SolCmd(object):
  """Deploy k8sdc solutions to the k8s cluster."""

  def parse(self, argv):
    args = docopt(__doc__, argv=argv)
    logger.debug("k8sdc sol - args:\n{}".format(args))
    self.tag = args['<solution>']

  def run(self):
    if self.tag is not None:
      self.tag = [self.tag]

    call_ansible(os.path.realpath(os.path.join(os.path.curdir, 'playbooks/sol.yaml')), 
                 tag = self.tag )
