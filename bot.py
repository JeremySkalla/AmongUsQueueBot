import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
player_queue = []

bot = commands.Bot(command_prefix="!") # Sets up bot

# Adds player to queue
@bot.command(
  brief = "adds player to queue"
)
async def queue(ctx):
  if ctx.message.author not in player_queue:
    player_queue.append(ctx.message.author)
    await ctx.channel.send(ctx.message.author.mention + ", you are #" + str(len(player_queue)) + " in the queue")
  else:
    await ctx.channel.send(ctx.message.author.mention + ", you are already in queue, use !unqueue to remove yourself from the queue")

# Removes player from queue if they don't want to play
@bot.command(
  brief = "removes player from queue"
)
async def unqueue(ctx):
  if ctx.message.author in player_queue:
    player_queue.remove(ctx.message.author)
    await ctx.channel.send(ctx.message.author.mention + " you have been removed from queue")
  else:
    await ctx.channel.send(ctx.message.author.mention + " you are not in queue, use !queue to add yourself to the queue")

# If the lobby needs more players, pings players in queue when spots are open
@bot.command(
  help = "pings players in queue when spots are open: num_spots is the amount of spots the lobby needs, and lobby is the lobby that needs the spots",
  brief = "pings players in queue when spots are open"
)
async def needplayer(ctx, num_spots=1, lobby=1):
  if len(player_queue) == 0:
    await ctx.channel.send("No players in queue currently")
  else:
    await ctx.channel.send("Lobby " + str(lobby) + " has " + str(num_spots) + " spot(s) open, if you are @ed below, please join!")
    i = 0
    for i in range(num_spots):
      if len(player_queue) == 0:
        break
      else:
        await ctx.channel.send(player_queue[0].mention)
        del player_queue[0]
      i += 1

# Displays # of users in queue
@bot.command(
  brief = "displays # of users in queue"
)
async def queuelength(ctx):
  await ctx.channel.send("There are " + str(len(player_queue)) + "s in queue")

# Checks how many players are ahead of user
@bot.command(
  brief = "checks how many players are ahead of user"
)
async def spotinqueue(ctx):
  if ctx.message.author in player_queue:
    await ctx.channel.send(ctx.message.author.mention + " you are currently #" + str(player_queue.index(ctx.message.author) + 1) + " in line")
  else:
    await ctx.channel.send(ctx.message.author.mention + " you are not in queue, please use !queue to join")
  
bot.run(TOKEN)