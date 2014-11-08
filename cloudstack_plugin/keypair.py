#########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

import os
import stat
import errno
import platform
from getpass import getuser
from libcloud.compute.types import Provider
from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError
from cloudstack_plugin.cloudstack_common import (
    delete_runtime_properties,
    get_resource_id,
    CLOUDSTACK_ID_PROPERTY,
    CLOUDSTACK_TYPE_PROPERTY,
    CLOUDSTACK_NAME_PROPERTY,
    COMMON_RUNTIME_PROPERTIES_KEYS,
    USE_EXTERNAL_RESOURCE_PROPERTY,
    get_cloud_driver
)

RUNTIME_PROPERTIES_KEYS = COMMON_RUNTIME_PROPERTIES_KEYS
KEYPAIR_CLOUDSTACK_TYPE = 'keypair'

PRIVATE_KEY_PATH_PROP = 'private_key_path'


@operation
def create(ctx, **kwargs):

    private_key_path = _get_private_key_path()
    pk_exists = _check_private_key_exists(private_key_path)

    if ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY] is True:
        if not pk_exists:
            delete_runtime_properties(ctx, RUNTIME_PROPERTIES_KEYS)
            raise NonRecoverableError(
                'Failed to use external keypair (node {0}): the public key {1}'
                ' is available on Openstack, but the private key could not be '
                'found at {2}'.format(ctx.node.id,
                                      ctx.node.properties['resource_id'],
                                      private_key_path))
        return

    if pk_exists:
        raise NonRecoverableError(
            "Can't create keypair - private key path already exists: {0}"
            .format(private_key_path))

    ctx.logger.info("Initializing {0} cloud driver"
                    .format(Provider.CLOUDSTACK))
    cloud_driver = get_cloud_driver(ctx)

    keypair = {
        'name': get_resource_id(ctx, KEYPAIR_CLOUDSTACK_TYPE),
    }
    keypair.update(ctx.node.properties['keypair'])
    #transform_resource_name(ctx, keypair)

    keypair = cloud_driver.create_key_pair(keypair['name'])

    # Cloudstack does not have an ID on keypair, so using name instead,
    # which is unique
    ctx.instance.runtime_properties[CLOUDSTACK_ID_PROPERTY] = keypair.name
    ctx.instance.runtime_properties[CLOUDSTACK_TYPE_PROPERTY] = \
        KEYPAIR_CLOUDSTACK_TYPE
    ctx.instance.runtime_properties[CLOUDSTACK_NAME_PROPERTY] = keypair.name

    try:
        # write private key file
        _mkdir_p(os.path.dirname(private_key_path))
        with open(private_key_path, 'w') as f:
            f.write(keypair.private_key)
            os.fchmod(f.fileno(), stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        _delete_private_key_file()
        delete_runtime_properties(ctx, RUNTIME_PROPERTIES_KEYS)
        raise


@operation
def delete(ctx, **kwargs):
    if not ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY]:
        ctx.logger.info('deleting keypair')

        _delete_private_key_file()

        ctx.logger.info("Initializing {0} cloud driver"
                        .format(Provider.CLOUDSTACK))
        cloud_driver = get_cloud_driver(ctx)

        key = get_key_pair(ctx, cloud_driver,
                                 ctx.instance.runtime_properties
                                 [CLOUDSTACK_ID_PROPERTY])
        cloud_driver.delete_key_pair(key_pair=key)
    else:
        ctx.logger.info('not deleting keypair since an external keypair is '
                        'being used')

    delete_runtime_properties(ctx, RUNTIME_PROPERTIES_KEYS)


@operation
def creation_validation(ctx, **kwargs):

    def validate_private_key_permissions(private_key_path):
        ctx.logger.debug('checking whether private key file {0} has the '
                         'correct permissions'.format(private_key_path))
        if not os.access(private_key_path, os.R_OK | os.W_OK):
            err = 'private key file {0} is not readable and/or ' \
                  'writeable'.format(private_key_path)
            ctx.logger.error('VALIDATION ERROR: ' + err)
            raise NonRecoverableError(err)
        ctx.logger.debug('OK: private key file {0} has the correct '
                         'permissions'.format(private_key_path))

    def validate_path_owner(path):
        ctx.logger.debug('checking whether directory {0} is owned by the '
                         'current user'.format(path))
        from pwd import getpwnam, getpwuid

        user = getuser()
        owner = getpwuid(os.stat(path).st_uid).pw_name
        current_user_id = str(getpwnam(user).pw_uid)
        owner_id = str(os.stat(path).st_uid)

        if not current_user_id == owner_id:
            err = '{0} is not owned by the current user (it is owned by {1})'\
                  .format(path, owner)
            ctx.logger.error('VALIDATION ERROR: ' + err)
            raise NonRecoverableError(err)
        ctx.logger.debug('OK: {0} is owned by the current user'.format(path))

    #validate_resource(ctx, nova_client, KEYPAIR_CLOUDSTACK_TYPE)

    private_key_path = _get_private_key_path()
    pk_exists = _check_private_key_exists(private_key_path)

    if ctx.node.properties[USE_EXTERNAL_RESOURCE_PROPERTY] is True:
        if pk_exists:
            if platform.system() == 'Linux':
                validate_private_key_permissions(private_key_path)
                validate_path_owner(private_key_path)
        else:
            err = "can't use external keypair: the public key {0} is " \
                  "available on Openstack, but the private key could not be " \
                  "found at {1}".format(ctx.node.properties['resource_id'],
                                        private_key_path)
            ctx.logger.error('VALIDATION ERROR: ' + err)
            raise NonRecoverableError(err)
    else:
        if pk_exists:
            err = 'private key path already exists: {0}'.format(
                private_key_path)
            ctx.logger.error('VALIDATION ERROR: ' + err)
            raise NonRecoverableError(err)

    ctx.logger.debug('OK: keypair configuration is valid')


def _get_private_key_path():
    return os.path.expanduser(ctx.node.properties[PRIVATE_KEY_PATH_PROP])


def _delete_private_key_file():
    private_key_path = _get_private_key_path()
    ctx.logger.debug('deleting private key file at {0}'.format(
        private_key_path))
    try:
        os.remove(private_key_path)
    except OSError as e:
        if e.errno == errno.ENOENT:
            # file was already deleted somehow
            pass
        raise


def _check_private_key_exists(private_key_path):
    return os.path.isfile(private_key_path)


def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise


def get_key_pair(ctx, cloud_driver, key_name):

    key = cloud_driver.get_key_pair(key_name)

    return key