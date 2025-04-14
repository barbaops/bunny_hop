import kopf
import logging
from handlers import queue

@kopf.on.startup()
def startup(settings: kopf.OperatorSettings, **_):
    settings.posting.level = logging.INFO 


