import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

#globals

TOKEN = os.getenv('DISCORD_TOKEN')

current_queues = []

bot = commands.Bot(command_prefix="!") # Sets up bot

#i'm definitely open to changing all the function names I wrote here. My goal was just to make them shorter to type, not set on them at all
"""
Current functionality:

!queue - adds user to queue if they aren't already and prints queue
!view - prints queue
!ping <num> - pings the first <num> users in line and dequeues them. If <num> is ommitted, pings the first person in line
!spot - tells the user how many people are ahead of them in queue (tells them their current spot)
!length - tells you the length of the current queue. probably not as useful as seeing the entire queue, but could still be good
!leave - dequeues the user if they are in queue

"""

#----------------------------------------
#             Queue Class
#----------------------------------------
class Queue:

  def __init__(self,name,ctx):
    #we can just default to 10-player queue for everything rn
    self.MAX = 10
    #create queue for game
    self.game = name
    self.queue = []

    #add this queue to the master list of all current queues
    current_queues.append(self)

  #helper function returns current queue as an embed. used in queue() and viewqueue()
  def print_queue(self):
      c = discord.Color.purple()
      t = "Queue for *{}*".format(self.game)
      d = ""

      for i in range(len(self.queue)):
          message = "**" +str(i+1) + ":** " + self.queue[i].name + "\n"
          d += message

      embed = discord.Embed(title=t,description=d,color=c)

      embed.set_footer(text="Use !queue {} to join the queue.".format(self.game))

      return embed

#----------------------------------------
#           Helper Functions
#----------------------------------------
def get_queue(name):
  for Queue in current_queues:
    if Queue.game == name:
      return Queue
  return False

def get_players_queue(player):
  for Queue in current_queues:
    if player in Queue.queue:
      return Queue
  return False

#----------------------------------------
#           Bot Commands
#----------------------------------------


#         Queue Function
#----------------------------------------
# Adds player to queue
@bot.command(
  brief = "adds player to queue and prints out the current queue",
  aliases = ['q']
)
async def queue(ctx,name="Among Us"):

  #if the queue doesn't exist, create one
  q = get_queue(name)
  if not q:
    q = Queue(name,ctx)
  
  #now, q is the queue we're working with. Either brand new or existing already

  #if the person is in the queue already, error. otherwise send message
  inq = False
  for person in q.queue:
    if ctx.message.author == person:
      await ctx.channel.send(ctx.message.author.mention + " you are already in queue. use !leave to remove yourself")
      inq = True
  #if they're not in the queue, add them
  if not inq:
    q.queue.append(ctx.message.author)
    await ctx.channel.send(ctx.message.author.mention + ", you are #" + str(len(q.queue)) + " in the queue")
      
  #no matter what, print out the queue now
  e = q.print_queue()
  await ctx.send(embed=e)


#         View Queue
#----------------------------------------
@bot.command(
    brief = "prints out the queue with a given name. Defaults to Among Us"
)
async def view(ctx,name="Among Us"):
  q = get_queue(name)
  if not q:
    await ctx.channel.send("Error: Please enter a valid queue name to view!")
    return
  
  e = q.print_queue()
  await ctx.channel.send(embed=e)


#         Ping for more players
#----------------------------------------
# If the lobby needs more players, pings players in queue when spots are open
@bot.command(
  help = "pings players in queue when spots are open: num_spots is the amount of spots the lobby needs, and lobby is the lobby that needs the spots",
  brief = "pings players in queue when spots are open. !ping <num> <name>"
)
async def ping(ctx,arg1=None,arg2=None):
  
  #TODO: dynamic thing so we can have name first. if the first thing is int, it's num_spots and not name
  name = ""
  num_spots = 0
  #neither argument is provided
  if not arg1 and not arg2:
    name = "Among Us"
    num_spots = 1
  #one argument is provided
  else:
    if arg1.isdigit():
      #arg 1 is num spots
      num_spots = int(arg1)
      if arg2:
        if arg2.isdigit():
          await ctx.channel.send("Error: cannot have two ints")
          return
        else:
          name = arg2
      else:
        #arg2 is auto among us
        name = "Among Us"
    else:
      #arg 1 is name
      name = arg1
      if arg2:
        if arg2.isdigit():
          num_spots = int(arg2)
        else:
          await ctx.channel.send("Error: cannot have two strings")
          return
      else:
        #arg 2 is auto "1" num spots
        num_spots = 1

  q = get_queue(name)
  if not q:
    await ctx.channel.send("Error: Please enter a valid queue name!")
    return
  
  if len(q.queue) == 0:
      e = discord.Embed(title="There are no players to ping. Sorry!")
      await ctx.channel.send(embed=e)
      return

  #if we get here, we have a valid queue with at least one player
  if num_spots == 1:
    t = "The lobby has 1 open spot!"
    d = "This player is next in line:\n"
  else:
    t = "The lobby has " + str(num_spots) + " open spots!"
    d = "These players are next in line:\n"
  
  d = "Please join if you are mentioned here."
  c = discord.Color.green()

  players = ""
  while num_spots > 0:
    if not q.queue:
        break
    player = q.queue.pop(0)
    players += player.mention + "\t"
    num_spots -= 1

  e = discord.Embed(title=t,description=d,color=c)

  await ctx.channel.send(embed=e)
  await ctx.channel.send(players)



#       Length function
#----------------------------------------
# Displays # of users in queue
@bot.command(
  brief = "displays # of users in queue"
)
async def length(ctx,name="Among Us"):
  q = get_queue(name)
  if not q:
    await ctx.channel.send("Error: Please enter a valid queue to view length")
    return
  
  await ctx.channel.send("There are " + str(len(q.queue)) + "s in queue")



#these functions use player-specific methods

#         Spot Function
#----------------------------------------
# Checks how many players are ahead of user
@bot.command(
  brief = "checks how many players are ahead of user"
)
async def spot(ctx):
  q = get_players_queue(ctx.message.author)
  if not q:
    await ctx.channel.send(ctx.message.author.mention + " you are currently not in any queue. Use !queue to join Among Us queue, or !queue <Name> to join another")
    return
  await ctx.channel.send(ctx.message.author.mention + " you are currently #" + str(q.queue.index(ctx.message.author) + 1) + " in line")
    

#       Leave Function
#----------------------------------------
# Removes player from queue if they don't want to play
@bot.command(
  brief = "removes player from queue"
)
async def leave(ctx):
  q = get_players_queue(ctx.message.author)
  if not q:
    await ctx.channel.send(ctx.message.author.mention + " you are currently not in any queue. Use !queue to join Among Us queue, or !queue <Name> to join another")
    return
  q.queue.remove(ctx.message.author)
  await ctx.channel.send(ctx.message.author.mention + " you have been removed from the {} queue".format(q.game))
  
#         Delete Function
#----------------------------------------
#removes a given queue from the master list
@bot.command(
  brief = "removes player from queue"
)
async def delete(ctx,name="Among Us"):
  q = get_queue(name)
  if not q:
    await ctx.channel.send("Error: please enter a valid queue name to delete")
    return
  current_queues.remove(q)
  await ctx.channel.send("Deleted the {} queue".format(q.game))


#     ViewAll Function
#----------------------------------------
#print out all current queues (mostly for debugging)
@bot.command(
  brief= "Prints out all active queues"
)
async def viewall(ctx):
  for Queue in current_queues:
    curr = Queue.print_queue()
    await ctx.channel.send(embed=curr)

bot.run(TOKEN)