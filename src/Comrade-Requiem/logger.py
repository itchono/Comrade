import logging
import datetime
from dis_snek.const import logger_name

logging.Formatter.converter = lambda *args: datetime.datetime.now().timetuple()

logger = logging.getLogger("ComradeLog")
logger.setLevel(logging.DEBUG)

# Configure loggers
c_handler = logging.StreamHandler()
# Console output
f_handler = logging.FileHandler(
    filename="comrade.log", mode="w", encoding="utf-8")
# Primary Log

c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

c_format = logging.Formatter('%(asctime)s: %(message)s',
                             datefmt="%H:%M:%S")
f_format = logging.Formatter('%(asctime)s [%(filename)s@%(lineno)d (%(funcName)s)]: %(levelname)s - %(message)s',
                             datefmt="%I:%M:%S %p")

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler)

logging.getLogger(logger_name).setLevel(logging.INFO)
logging.getLogger(logger_name).addHandler(f_handler)
 