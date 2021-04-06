import logging
from utils.utilities import local_time

logging.Formatter.converter = lambda *args: local_time().timetuple()

logger = logging.getLogger("ComradeLog")
logger.setLevel(logging.DEBUG)

# Configure loggers
c_handler = logging.StreamHandler()
# Console output
f_handler1 = logging.FileHandler(
    filename="comrade_primary.log", mode="w", encoding="utf-8")
# Primary Log
f_handler2 = logging.FileHandler(
    filename="comrade_full.log", mode="w", encoding="utf-8")
# Full Log with Flask and Discord

c_handler.setLevel(logging.INFO)
f_handler1.setLevel(logging.DEBUG)
f_handler2.setLevel(logging.DEBUG)

c_format = logging.Formatter('%(asctime)s: %(message)s',
                             datefmt="%H:%M:%S")
f_format = logging.Formatter('%(asctime)s [%(filename)s@%(lineno)d (%(funcName)s)]: %(levelname)s - %(message)s',
                             datefmt="%I:%M:%S %p")

c_handler.setFormatter(c_format)
f_handler1.setFormatter(f_format)
f_handler2.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler1)
logger.addHandler(f_handler2)

logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("discord").addHandler(f_handler2)

logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('werkzeug').addHandler(f_handler2)
