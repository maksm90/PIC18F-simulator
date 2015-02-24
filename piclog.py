import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter('*** %(levelname)-8s %(message)s'))
logger.addHandler(ch)
