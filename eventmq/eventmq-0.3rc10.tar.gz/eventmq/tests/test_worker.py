# This file is part of eventmq.
#
# eventmq is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# eventmq is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with eventmq.  If not, see <http://www.gnu.org/licenses/>.
import time

from .. import conf, constants, worker
from nose import with_setup
from multiprocessing import Pool

ADDR = 'inproc://pour_the_rice_in_the_thing'


def setup_func():
    global pool
    global out
    pool = Pool()
    out = pool.map(job, range(1))

@with_setup(setup_func)
def test_run_with_timeout():
    payload = {
        'path': 'eventmq.tests.test_worker',
        'callable': 'job',
        'args': [2]
    }

    msgid = worker._run(payload)


def job(sleep_time=0):
    time.sleep(sleep_time)

    return True
