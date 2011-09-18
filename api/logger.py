import logging

logger = logging.getLogger('Builder')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)