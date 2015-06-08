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

from cloudify.decorators import operation

from cloudstack_exoscale_plugin.cloudstack_common import get_cloud_driver


@operation
def create(ctx, **kwargs):
    """ Create security group with rules.
    """

    cloud_driver = get_cloud_driver(ctx)

    security_group = {
        'description': None,
        'name': ctx.node_id,
    }

    ctx.logger.debug('reading security-group configuration.')
    rules_to_apply = ctx.node.properties['rules']
    security_group.update(ctx.node.properties['security_group'])

    security_group_name = security_group['name']
    if not _sg_exists(cloud_driver, security_group_name):
        ctx.logger.info('creating security group: {0}'
                        .format(security_group_name))
        cloud_driver.ex_create_security_group(
            security_group_name,
            description=security_group['description'])
        for rule in rules_to_apply:
            cidr = rule.get('cidr', None)
            protocol = rule.get('protocol', 'TCP')
            start_port = rule.get('start_port', None)
            if start_port is None:
                raise RuntimeError(
                    'You must specify start_port for a security group rule')
            end_port = rule.get('end_port', None)
            _add_ingress_rule(ctx, cloud_driver,
                              security_group_name=security_group_name,
                              start_port=start_port,
                              end_port=end_port,
                              cidr_list=cidr,
                              protocol=protocol)
    else:
        ctx.logger.info('using existing management security group {0}'.format(
            security_group_name))


@operation
def delete(ctx, **kwargs):
    try:
        cloud_driver = get_cloud_driver(ctx)
        cloud_driver.ex_delete_security_group(ctx.instance.runtime_properties[
            'external_id'])
    except:
        ctx.logger.warn(
            'security-group {0} may not have been deleted'
            .format(ctx.instance.runtime_properties['external_id']))


def _sg_exists(cloud_driver, security_group_name):
    exists = get_security_group(cloud_driver, security_group_name)
    if not exists:
        return False
    return True


def get_security_group(cloud_driver, security_group_name):
    security_groups = [
        sg for sg in cloud_driver.ex_list_security_groups()
        if sg['name'] == security_group_name]
    if security_groups.__len__() == 0:
        return None
    return security_groups[0]


def _add_ingress_rule(ctx, cloud_driver, security_group_name, protocol,
                      cidr_list,
                      start_port,
                      end_port=None):

    ctx.logger.debug('creating security-group rule for {0} with details {1}'
                     .format(security_group_name, locals().values()))
    cloud_driver.ex_authorize_security_group_ingress(
        securitygroupname=security_group_name,
        startport=start_port,
        endport=end_port,
        cidrlist=cidr_list,
        protocol=protocol)
