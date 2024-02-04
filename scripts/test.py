@velt.command()
async def firecode(ctx, message):
    await notif.send(message)
    await ctx.send("Sent to Firecode!")