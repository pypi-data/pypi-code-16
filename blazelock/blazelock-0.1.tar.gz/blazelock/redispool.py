# Copyright 2016 Kunal Lillaney (http://kunallillaney.github.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import redis
from singletontype import SingletonType

class RedisPool(object):
  __metaclass__ = SingletonType 
  blocking_pool = None

  def __init__(self, host='localhost', port=6379, db=0, max_connections=10):
    print "entering init"
    blocking_pool = redis.BlockingConnectionPool(host=host, port=port, db=db, max_connections=max_connections)
