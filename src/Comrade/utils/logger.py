import logging


logger = logging.getLogger("ComradeLog")
logger.setLevel(logging.INFO)

# Configure loggers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(
    filename="comrade.log", mode="w", encoding="utf-8")
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

c_format = logging.Formatter('%(asctime)s: %(message)s',
                             datefmt="%H:%M:%S")
f_format = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s',
                             datefmt="%I:%M:%S %p %Z")

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler)

# async def log(guild, m: str, embed=None):
#     '''
#     Logs a message in the server's log-channel in a clean embed form, or sends a pre-made embed.
#     '''
#     if lgc := await getChannel(guild, "log-channel"):
#         if not embed:
#             embed = dscord.Embed(title="Log Entry", description=m)
#             embed.add_field(name="Time", value=(localTime().strftime("%I:%M:%S %p %Z")))
#         await lgc.send(embed=embed)
