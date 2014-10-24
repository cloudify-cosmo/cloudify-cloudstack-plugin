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
from cloudstack_plugin.cloudstack_common import get_cloud_driver
from network import get_network
from cloudify.exceptions import NonRecoverableError


__author__ = 'boul'


@operation
def create(ctx, **kwargs):

    cloud_driver = get_cloud_driver(ctx)

    floatingip = {
        # No defaults
    }
    floatingip.update(ctx.properties['floatingip'])

    # ctx.logger.debug('getting id for:{0}'.format(
    #     floatingip['floating_network_name']))
    # vpc_result = get_network(
    #     cloud_driver, floatingip['floating_network_name'])
    # ctx.logger.info(repr(vpc_result))
    #
    # ctx.logger.info('getting id for:{0} networkid {1}, vpcid{2}'.format(
    #     floatingip['floating_network_name'], vpc_result.id,
    #     vpc_result.extra['vpc_id']))

    # get the ID's
    if 'floating_network_name' in floatingip:
        floatingip['floating_network_vpc_id'] = get_network(
            cloud_driver, floatingip['floating_network_name']
        ).extra['vpc_id']

        floatingip['floating_network_id'] = get_network(
            cloud_driver, floatingip['floating_network_name']).id
    else:
        raise NonRecoverableError('floating_network_name, not specified?')

    # If we get a vpc-id let's use that otherwise use the network-id
    if floatingip['floating_network_vpc_id'] is not None:

        ctx.logger.info('Acquiring IP for VPC with id: {0}'.format(floatingip[
            'floating_network_vpc_id']))
        
        fip = cloud_driver.ex_allocate_public_ip(vpc_id=floatingip[
            'floating_network_vpc_id'])

    elif floatingip['floating_network_id'] is not None:

        ctx.logger.info('Acquiring IP for VPC with id: {0}'.format(floatingip[
            'floating_network_id']))

        fip = cloud_driver.ex_allocate_public_ip(network_id=floatingip[
            'floating_network_id'])

    else:
        raise NonRecoverableError('Cannot resole network or vpc id')

    ctx.runtime_properties['external_id'] = fip.id
    ctx.runtime_properties['external_type'] = 'publicip'
    ctx.runtime_properties['floating_ip_address'] = fip.address




# @operation
# def delete(ctx, **kwargs):