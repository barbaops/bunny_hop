import kopf
from handlers import queue, exchange, binding, shovel
import logging

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = logging.INFO
