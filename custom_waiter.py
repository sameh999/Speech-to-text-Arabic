
from enum import Enum
import logging
import botocore.waiter

logger = logging.getLogger(__name__)
class WaitState(Enum):
    SUCCESS = 'success'
    FAILURE = 'failure'

class CustomWaiter:
    def __init__(
            self, name, operation, argument, acceptors, client, delay=10, max_tries=100,
            matcher='path'):

        self.name = name
        self.operation = operation
        self.argument = argument
        self.client = client
        self.waiter_model = botocore.waiter.WaiterModel({
            'version': 2,
            'waiters': {
                name: {
                    "delay": delay,
                    "operation": operation,
                    "maxAttempts": max_tries,
                    "acceptors": [{
                        "state": state.value,
                        "matcher": matcher,
                        "argument": argument,
                        "expected": expected
                    } for expected, state in acceptors.items()]
                }}})
        self.waiter = botocore.waiter.create_waiter_with_client(
            self.name, self.waiter_model, self.client)

    def __call__(self, parsed, **kwargs):
        status = parsed
        for key in self.argument.split('.'):
            if key.endswith('[]'):
                status = status.get(key[:-2])[0]
            else:
                status = status.get(key)
        logger.info(
            "Waiter %s called %s, got %s.", self.name, self.operation, status)

    def _wait(self, **kwargs):
        event_name = f'after-call.{self.client.meta.service_model.service_name}'
        self.client.meta.events.register(event_name, self)
        self.waiter.wait(**kwargs)
        self.client.meta.events.unregister(event_name, self)
