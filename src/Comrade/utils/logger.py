import logging
from utils.utilities import local_time

logging.Formatter.converter = lambda *args: local_time().timetuple()

logger = logging.getLogger("ComradeLog")
logger.setLevel(logging.DEBUG)

# Configure loggers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(
    filename="comrade.log", mode="w", encoding="utf-8")
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

c_format = logging.Formatter('%(asctime)s: %(message)s',
                             datefmt="%H:%M:%S")
f_format = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s',
                             datefmt="%I:%M:%S %p %Z")

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler)

logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("discord").addHandler(f_handler)

logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('werkzeug').addHandler(f_handler)
