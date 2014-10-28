########
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


from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from cloudstack_plugin.cloudstack_common import get_cloud_driver, \
     get_network_by_id, get_floating_ip_by_id


__author__ = 'boul'


@operation
def connect_network(ctx, **kwargs):

    cloud_driver = get_cloud_driver(ctx)

    network_id = ctx.related.runtime_properties['network_id']
    network = get_network_by_id(ctx, cloud_driver, network_id)

    if network.extra['vpc_id'] is not None:

        ctx.logger.info('Acquiring IP for VPC with id: {0}'
                        .format(network.extra['vpc_id']))

        fip = cloud_driver.ex_allocate_public_ip(vpc_id=
                                                 network.extra['vpc_id'])

    elif network.id is not None:

        ctx.logger.info('Acquiring IP for network with id: {0}'.
                        format(network.id))

        fip = cloud_driver.ex_allocate_public_ip(network_id=network.id)

    else:
        raise NonRecoverableError('Cannot resolve network or vpc id')

    ctx.instance.runtime_properties['external_id'] = fip.id
    ctx.instance.runtime_properties['external_type'] = 'publicip'
    ctx.instance.runtime_properties['floating_ip_address'] = fip.address


@operation
def disconnect_network(ctx, **kwargs):

    cloud_driver = get_cloud_driver(ctx)

    fip_id = ctx.instance.runtime_properties['external_id']
    fip = get_floating_ip_by_id(ctx, cloud_driver, fip_id)

    ctx.logger.info('Deleting floating ip: {0}'.format(fip))

    cloud_driver.ex_release_public_ip(address=fip)

