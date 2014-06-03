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
import copy
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import libcloud.security

__author__ = 'uri1803'

def _get_auth_from_context(ctx):
    auth_config = {}
    auth_config.update(copy.deepcopy(ctx.properties['auth']))
    return auth_config


def get_cloud_driver(ctx):
    auth_config = _get_auth_from_context(ctx)
    api_key = auth_config['API_KEY']
    api_secret_key = auth_config['API_SECRET_KEY']
    driver = get_driver(Provider.EXOSCALE)
    libcloud.security.VERIFY_SSL_CERT = False
    return driver(api_key, api_secret_key)


