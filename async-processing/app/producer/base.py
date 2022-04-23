import json
import os
import uuid
from typing import Literal

import pika
from logger import get_logger

LOGGER = get_logger()

# Possible values as queue name
QueueNames = Literal['queue.model.train', 'queue.model.predict']
RepQueueNames = Literal['queue.reply.train', 'queue.reply.predict']


class BaseProducer:
    def __init__(self, queue_name: QueueNames, rep_queue_name: RepQueueNames):
        self.queue_name = queue_name
        self.rep_queue_name = rep_queue_name
        self.pika_params = pika.ConnectionParameters(
            host="rabbitmq",
            port=os.getenv('RABBITMQ_PORT', 5672),
            connection_attempts=10,
            heartbeat=0
        )
        self.connection = pika.BlockingConnection(self.pika_params)
        self.channel = self.connection.channel()
        LOGGER.info('Pika connection initialized.')

        result = self.channel.queue_declare(queue=self.rep_queue_name, exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def send_message_to_consumer(self, message: dict):
        """Send message

        Args:
            message (dict): message info
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        message_json = json.dumps(message)

        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=message_json,
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2,  # make message persistent
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            )
        )

        LOGGER.info(f"Sent message. [q] '{self.queue_name}' [x] Body: {message_json=}")

        while self.response is None:
            self.connection.process_data_events()

        self.close()
        return self.response

    def close(self):
        self.channel.close()
        self.connection.close()
