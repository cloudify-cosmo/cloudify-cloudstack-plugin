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

from cloudstack_plugin.cloudstack_common import (
    get_cloud_driver,
    CLOUDSTACK_ID_PROPERTY,
    CLOUDSTACK_TYPE_PROPERTY,
    COMMON_RUNTIME_PROPERTIES_KEYS

)
from cloudstack_plugin.network import get_network_by_id


FLOATINGIP_CLOUDSTACK_TYPE = 'floatingip'

# Runtime properties
IP_ADDRESS_PROPERTY = 'floating_ip_address'
RUNTIME_PROPERTIES_KEYS = COMMON_RUNTIME_PROPERTIES_KEYS + \
    [IP_ADDRESS_PROPERTY]


@operation
def connect_network(ctx, **kwargs):

    cloud_driver = get_cloud_driver(ctx)

    network_id = ctx.target.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    network = get_network_by_id(ctx, cloud_driver, network_id)

    if network.extra['vpc_id'] is not None:

        ctx.logger.info('Acquiring IP for VPC with id: {0}'
                        .format(network.extra['vpc_id']))

        fip = cloud_driver.ex_allocate_public_ip(
            vpc_id=network.extra['vpc_id'])

    elif network.id is not None:

        ctx.logger.info('Acquiring IP for network with id: {0}'.
                        format(network.id))

        fip = cloud_driver.ex_allocate_public_ip(network_id=network.id)

        if 'firewall' in ctx.target.node.properties:
                firewall_config = ctx.target.node.properties['firewall']

                ingress_rules = [rule for rule in firewall_config
                                 if rule['type'] == 'ingress']

                for rule in ingress_rules:
                    rule_cidr = rule.get('cidr')
                    rule_protocol = rule.get('protocol')
                    rule_ports = rule.get('ports')

                    for port in rule_ports:
                        ctx.logger.info('Creating ingress fw rule:'
                                        ' {3}:{0}:{1}-{2}'
                                        .format(rule_cidr,
                                                port,
                                                port,
                                                rule_protocol))

                        cloud_driver.ex_create_firewall_rule(
                            address=fip,
                            cidr_list=rule_cidr,
                            protocol=rule_protocol,
                            start_port=port,
                            end_port=port
                        )

    else:
        raise NonRecoverableError('Cannot resolve network or vpc id')

    ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = fip.id
    ctx.source.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
        FLOATINGIP_CLOUDSTACK_TYPE
    ctx.source.instance.runtime_properties[IP_ADDRESS_PROPERTY] = fip.address


@operation
def disconnect_network(ctx, **kwargs):

    cloud_driver = get_cloud_driver(ctx)

    fip_id = ctx.source.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY]
    fip = get_floating_ip_by_id(ctx, cloud_driver, fip_id)

    firewall_rules = [rule for rule in cloud_driver.ex_list_firewall_rules()
                      if fip.id == rule.address.id]

    for rule in firewall_rules:

        ctx.logger.info('Deleting fw rule: {3}:{0}:{1}-{2}'.format(
            rule.cidr_list, rule.start_port, rule.end_port, rule.protocol))

        cloud_driver.ex_delete_firewall_rule(rule)

    ctx.logger.info('Deleting floating ip: {0}'.format(fip))

    try:
        cloud_driver.ex_release_public_ip(address=fip)
    except Exception as e:
        ctx.logger.warn('Floating IP: {0} may not have been deleted: {1}'
                        .format(fip, str(e)))
        pass


def get_floating_ip_by_id(ctx, cloud_driver, floating_ip_id):

    fips = [fip for fip in cloud_driver.ex_list_public_ips()
            if floating_ip_id == fip.id]

    if not fips:
        ctx.logger.info('could not find floating ip by ID {0}'.
                        format(floating_ip_id))
        return None

    return fips[0]
