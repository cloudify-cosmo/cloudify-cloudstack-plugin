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

    ctx.logger.debug('getting id for:{0}'.format(
        floatingip['floating_network_name']))
    vpc_result = get_network(
        cloud_driver, floatingip['floating_network_name'])
    ctx.logger.info(repr(vpc_result))

    ctx.logger.info('getting id for:{0} networkid {1}, vpcid{2}'.format(
        floatingip['floating_network_name'], vpc_result.id,
        vpc_result.extra['vpc_id']))

    # Check if network belongs to a VPC if so, we need it's id.
    if 'floating_network_name' in floatingip:
        floatingip['floating_network_vpc_id'] = get_network(
            cloud_driver, floatingip['floating_network_name']
        ).extra['vpc_id']

    # Not belonging to a VPC then we need the network id.
    elif 'floating_network_vpc_id' not in floatingip:
        floatingip['floating_network_id'] = get_network(
            cloud_driver, floatingip['floating_network_name,']).id

    else:
        raise NonRecoverableError('Cannot find the vpc_id or network_id, '
                                  'Does this network exist?')
    #
    #  # Sugar: floating_network_name -> (resolve) -> floating_network_id
    # if 'floating_network_name' in floatingip:
    #     floatingip['floating_network_id'] = neutron_client.cosmo_get_named(
    #         'network', floatingip['floating_network_name'])['id']
    #     del floatingip['floating_network_name']
    # elif 'floating_network_id' not in floatingip:
    #     provider_context = provider(ctx)
    #     ext_network = provider_context.ext_network
    #     if ext_network:
    #         floatingip['floating_network_id'] = ext_network['id']
    # else:
    #     raise NonRecoverableError('Missing floating network id or name')

    if floatingip['floating_network_vpc_id'] is not None:
        args = {'vpc_id' : floatingip['floating_network_vpc_id']}
    else:
        args = {'network_id': floatingip['floating_network_id']}

    fip = cloud_driver.ex_allocate_public_ip(args)

    ctx.runtime_properties[external_id] = fip['id']
    ctx.runtime_properties[external_type] = 'publicip'
    ctx.runtime_properties[floating_ip_address] = fip['address']




# @operation
# def delete(ctx, **kwargs):