########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

import unittest

__author__ = 'adaml'

from exoscale_plugin.exoscale_plugin import start
from exoscale_plugin.exoscale_plugin import stop
from exoscale_plugin.exoscale_plugin import delete
from exoscale_plugin.exoscale_plugin import get_state

from cloudify.mocks import MockCloudifyContext

class ExoscalePluginTestCase(unittest.TestCase):

    def test_start_server(self):
        context = MockCloudifyContext(
            node_id='id',
            properties={'server':
                            {
                                'name' : 'adaml2-cloudify-exoscale-testing-vm',
                                'image_id' : '70d31a38-c030-490b-bca9-b9383895ade7',
                                'key_name' : 'cloudify-agents-kp',
                                'security_groups' :['cloudify-sg-agents', ],
                                'size' : 'Micro'
                            },
                        'auth':
                            {
                                'API_KEY': '8rVa1PQ6GIchsNgzryI-NGDXO-n9NbI-9fKmvQcW-JfK6D4z8z4RlNdSQ4aD3Mpk2iBgrMzQuP7mHv88f6mTlg',
                                'API_SECRET_KEY' : 'y2saZqfYPencTkLoEhMa8m-ZZ58L8Gq5m4ojQZhKONljsKtJW0RZuvKKmRUO0HCsjSzM3VdyeY_2_011Usrd4A',
                            }
            })
        start(context)
        state_after_start = get_state(context)
        if not state_after_start:
            raise AssertionError('expecting get_state to return true '
                                 'since server is up.')
        stop(context)
        delete(context)
        state_after_termination = get_state(context)
        if state_after_termination:
            raise AssertionError('expecting get_state to return false '
                                 'since server is down.')






