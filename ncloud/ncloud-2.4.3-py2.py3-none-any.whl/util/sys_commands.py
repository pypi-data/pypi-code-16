# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
Utils to run system commands
"""
import os
import errno


def create_all_dirs(local_file):
    local_file_dirname = os.path.dirname(local_file)
    if not os.path.exists(local_file_dirname):
        try:
            os.makedirs(local_file_dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
