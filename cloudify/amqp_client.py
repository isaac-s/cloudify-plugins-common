########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.


import json
import pika

from cloudify import ctx
from cloudify.utils import get_manager_ip


class AMQPClient(object):

    events_queue_name = 'cloudify-events'
    logs_queue_name = 'cloudify-logs'

    def __init__(self):
        self._reconnect()

    def publish_log(self, log):
        self._publish(log, self.logs_queue_name)

    def publish_event(self, event):
        self._publish(event, self.events_queue_name)

    def close(self):
        if self.connection:
            self.connection.close()

    def _reconnect(self):
        try:
            self.close()
        except:
            ctx.logger.warn('Failed closing connection')

        self.connection = None
        self.events_queue = None
        self.logs_queue = None
        credentials = pika.PlainCredentials('cloudify', 'c10udify')
        ctx.logger.info('Establishing connection...')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=get_manager_ip(),
                                      credentials=credentials))
        ctx.logger.info('Connection established; establishing channels...')
        settings = {
            'auto_delete': True,
            'durable': True,
            'exclusive': False
        }
        self.logs_queue = self.connection.channel()
        self.logs_queue.queue_declare(queue=self.logs_queue_name, **settings)
        self.events_queue = self.connection.channel()
        self.events_queue.queue_declare(queue=self.logs_queue_name, **settings)
        ctx.logger.info('Channels established; all done.')

    def _publish(self, item, queue):
        if not self.connection.is_open():
            ctx.logger.info('Connection closed; reconnecting...')
            self._reconnect()
            ctx.logger.info('Reconnected')

        self.events_queue.basic_publish(exchange='',
                                        routing_key=queue,
                                        body=json.dumps(item))


def create_client():
    return AMQPClient()
