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


from cloudstack_exoscale_plugin.virtual_machine import start
from cloudstack_exoscale_plugin.virtual_machine import stop
from cloudstack_exoscale_plugin.virtual_machine import delete
from cloudstack_exoscale_plugin.virtual_machine import get_state
from cloudstack_exoscale_plugin.security_group import (
    create as create_security_group)

from cloudify.mocks import MockCloudifyContext


class ExoscalePluginTestCase(unittest.TestCase):

    def test_create_vm(self):
        context = MockCloudifyContext(
            node_id='id',
            properties={'server':
                        {
                            'name': 'adaml2-cloudify-exoscale-testing-vm',
                            'image_id': '70d31a38-c030-490b-bca9-b9383895ade7',
                            'keypair_name': 'cloudify-agents-kp',
                            'security_groups': ['cloudify-agents-sg', ],
                            'size': 'Medium'
                        },
                        'auth':
                            {
                                'API_KEY': 'API_KEY',
                                'API_SECRET_KEY': 'API_SECRET_KEY', }})
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

    def test_create_security_group(self):
        ctx = MockCloudifyContext(
            node_id='id',
            properties={'security_group':
                        {
                            'name': 'uri_test_sec_group',
                            'description': 'Test security group'
                        },
                        'auth':
                            {
                                'API_KEY': 'API_KEY',
                                'API_SECRET_KEY': 'API_SECRET_KEY', },
                        'rules':
                            [
                                {'cidr': '0.0.0.0/0', 'start_port': 27017,
                                 'protocol': 'TCP'},
                                {'cidr': '0.0.0.0/0', 'start_port': 28017,
                                 'protocol': 'TCP'}]})
        create_security_group(ctx)
