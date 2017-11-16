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
from pprint import pformat
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError, RecoverableError
from cloudify.decorators import operation
from openstack_plugin_common import with_nova_client


#ctx.instance.runtime_properties['mine'] = 'mashoe'
# random note regarding nova floating-ips: floating ips on nova-net have
# pre-assigned ids, and thus a call "nova.floating_ips.get(<fip_id>)" will
# return a value even if the floating-ip isn't even allocated.
# currently all lookups in the code, including by id, use search (i.e.
# nova.<type>.findall) and lists, which won't return such unallocated
# resources.

@operation
@with_nova_client
def get(nova_client, args, **kwargs):

    limits =  nova_client.limits.get()

    for alimit in limits.absolute:
        ctx.instance.runtime_properties[alimit.name] = alimit.value


@operation
@with_nova_client
def check(nova_client, check_limits, **kwargs):

    check_limits = ctx.node.properties['check_limits']

    for check_limit in check_limits:
        result = False
        available = 0
        value= int(check_limit['value'])

        ctx.logger.info('Checking Limit {0}'.format(check_limit['name']))

        # Code fot methode of calculation by_max_used_limit
        if check_limit['calculate'] == 'by_max_used_limit':
            available = ctx.instance.runtime_properties[check_limit['max']] -  ctx.instance.runtime_properties[check_limit['used']]
            if available - value > 0 :
                 result = True


        # update resutl to runtime_props
        ctx.instance.runtime_properties[check_limit['name']] = result

        if result:

             ctx.logger.info('Limit Passed {0} Required :{1} Available:{2}  '.format(check_limit['name'],  value , available))
        else:

             #if it's ahard limit fail workflow else logg
             if check_limit['type'] == 'hard':
                 raise NonRecoverableError('Hard Limit failiure, Limit {0} Required :{1} Available:{2}  '.format(check_limit['name'],  value, available))
             else:
                 ctx.logger.warn('Limit Failed {0} Required :{1} Available:{2}  '.format(check_limit['name'],  value, available))
