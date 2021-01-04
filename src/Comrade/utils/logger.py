# async def log(guild, m: str, embed=None):
#     '''
#     Logs a message in the server's log-channel in a clean embed form, or sends a pre-made embed.
#     '''
#     if lgc := await getChannel(guild, "log-channel"):
#         if not embed:
#             embed = dscord.Embed(title="Log Entry", description=m)
#             embed.add_field(name="Time", value=(localTime().strftime("%I:%M:%S %p %Z")))
#         await lgc.send(embed=embed)