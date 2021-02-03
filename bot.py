import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

# Globals
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
current_queues = []

bot = commands.Bot(command_prefix="!")  # Sets up bot

# i'm definitely open to changing all the function names I wrote here. My goal was just to make them shorter to type, not set on them at all
"""
Current functionality:

!queue - adds user to queue if they aren't already and prints queue
!view - prints queue
!ping <num> - pings the first <num> users in line and dequeues them. If <num> is ommitted, pings the first person in line
!spot - tells the user how many people are ahead of them in queue (tells them their current spot)
!length - tells you the length of the current queue. probably not as useful as seeing the entire queue, but could still be good
!leave - dequeues the user if they are in queue
"""

# ----------------------------------------
#             Queue Class
# ----------------------------------------

class Queue:
    # Initialization
    def __init__(self, name, ctx):
        # Default to 10-player queue for everything
        self.MAX = 10
        # Create queue for game
        self.game = name
        self.queue = []

        # Add this queue to the master list of all current queues
        current_queues.append(self)

    # Mutators
    def set_max(self, new_max):
        self.MAX = new_max

    # Helper function returns current queue as an embed -- Used in queue() and viewqueue()
    def print_queue(self):
        c = discord.Color.purple()
        t = "Queue for *{}*".format(self.game)
        d = ""

        for i in range(len(self.queue)):
            message = "**" + str(i+1) + ":** " + self.queue[i].name + "\n"
            d += message

        embed = discord.Embed(title=t, description=d, color=c)
        embed.set_footer(
            text="Use !queue {} to join the queue.".format(self.game))

        return embed

# ----------------------------------------
#            Helper Functions
# ----------------------------------------

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

# If the queue is 10 players long
def create_new_lobby(queue):
    # TODO NEXT VERSION
    return

# ----------------------------------------
#              Bot Commands
# ----------------------------------------

# Queue function
@bot.command(
    help = "Adds player to queue and prints out the current queue -- Use: !queue -- Other Names: !q, !que, !queue, !joinqueue, !cue",
    brief = "Adds player to queue and prints out the current queue -- Use: !queue",
    aliases = ['q', 'que', 'joinqueue', 'cue']
)
async def queue(ctx, name="Among Us"):
    # If the queue doesn't exist, create one
    q = get_queue(name)
    if not q:
        q = Queue(name, ctx)

    # Check if the person is in the queue already
    inq = False
    for person in q.queue:
        if ctx.message.author == person:
            await ctx.channel.send(ctx.message.author.mention + " you are already in queue. use !leave to remove yourself")
            inq = True
    # If they're not in the queue, add them
    if not inq:
        q.queue.append(ctx.message.author)
        await ctx.channel.send(ctx.message.author.mention + ", you are #" + str(len(q.queue)) + " in the queue")
    
    e = q.print_queue()
    await ctx.send(embed=e)

# Removes player from queue if they don't want to play
@bot.command(
    help = "Removes player from queue -- Default Input: \"Among Us\" -- Use: !unqueue <name> -- Other Names: !unq, !unque, !leave, !leaveq, !leaveque, !leavequeue, !dq, !deq, !deque, !dequeue",
    brief = "Removes player from queue -- Default Input: \"Among Us\" -- Use: !unqueue <name>",
    aliases = ['unq', 'unque', 'leave', 'leaveq', 'leaveque', 'leavequeue', 'dq', 'deq', 'deque', 'dequeue']
)
async def unqueue(ctx, name="Among Us"):
    q = get_queue(name)
    if not q:
        await ctx.channel.send(ctx.message.author.mention + " you are currently not in that queue. Use !queue to join Among Us queue, or !queue <Name> to join another")
        return
    q.queue.remove(ctx.message.author)
    await ctx.channel.send(ctx.message.author.mention + " you have been removed from the {} queue".format(q.game))
    
# If the lobby needs more players, pings players in queue when spots are open
@bot.command(
    help = "Pings players in queue when spots are open -- Default Input: NONE -- Use: !ping <num> <name> -- Other Names: !ping, !pingplayer, !need, !needplayer",
    brief = "Pings players in queue when spots are open -- Default Input: NONE -- Use: !ping <num> <name>",
    aliases = ['need', 'needplayer', 'pingplayer']
)
async def ping(ctx, arg1=None, arg2=None):
    # This code accounts for any ordering of the arguments
    name = ""
    num_spots = 0
    # neither argument is provided
    if not arg1 and not arg2:
        name = "Among Us"
        num_spots = 1
    # One argument is provided
    else:
        # Arg 1 is num
        if arg1.isdigit():
            num_spots = int(arg1)
            if arg2:
                if arg2.isdigit():
                    await ctx.channel.send("Error: cannot have two ints")
                    return
                else:
                    name = arg2
            # Arg2 is auto among us
            else:
                name = "Among Us"
        # Arg 1 is name
        else:
            name = arg1
            if arg2:
                if arg2.isdigit():
                    num_spots = int(arg2)
                else:
                    await ctx.channel.send("Error: cannot have two strings")
                    return
            # Arg 2 is auto "1" num spots
            else:
                num_spots = 1

    q = get_queue(name)
    if not q:
        await ctx.channel.send("Error: Please enter a valid queue name!")
        return

    if len(q.queue) == 0:
        e = discord.Embed(title="There are no players to ping. Sorry!")
        await ctx.channel.send(embed=e)
        return

    # If we get here, we have a valid queue with at least one player
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
        players += player.mention + " "
        num_spots -= 1

    e = discord.Embed(title=t, description=d, color=c)

    await ctx.channel.send(embed=e)
    await ctx.channel.send(players)

# Prints out queue with given name
@bot.command(
    help = "Prints out the queue with its name -- Default Input: \"Among Us\" -- Use: !view <game> -- Other Names: !view, !viewq, !viewqueue, !print, !printq, !printqueue",
    brief = "Prints out the queue with its name -- Default Input: \"Among Us\" -- Use: !view <game>",
    aliases = ['print', 'printq', 'printqueue', 'viewq', 'viewqueue'])
async def view(ctx, name="Among Us"):
    q = get_queue(name)
    if not q:
        await ctx.channel.send("Error: Please enter a valid queue name to view!")
        return

    e = q.print_queue()
    await ctx.channel.send(embed=e)

# Displays # of users in queue
@bot.command(
    help = "Displays # of users in queue -- Default Input: \"Among Us\" -- Use: !length <name> -- Other Names: !qlength, !quelength, !queuelength",
    brief = "Displays # of users in queue -- Default Input: \"Among Us\" -- Use: !length <name> ",
    aliases = ['qlength', 'quelength', 'queuelength']
)
async def length(ctx, name="Among Us"):
    q = get_queue(name)
    if not q:
        await ctx.channel.send("Error: Please enter a valid queue to view length")
        return

    await ctx.channel.send("There are " + str(len(q.queue)) + "s in queue")

# Checks how many players are ahead of user
@bot.command(
    help = "Displays how many players are ahead of user -- Use: !spot -- Other Names: !spotinq, !spotinque, !spotinqueue, !place, !placeinq, !placeinque, !placeinqueue",
    brief = "Displays how many players are ahead of user -- Use: !spot",
    aliases = ['spotinq', 'spotinque', 'spotinqueue', 'place', 'placeinq', 'placeinque', 'placeinqueue']
)
async def spot(ctx):
    q = get_players_queue(ctx.message.author)
    if not q:
        await ctx.channel.send(ctx.message.author.mention + " you are currently not in any queue. Use !queue to join Among Us queue, or !queue <Name> to join another")
        return
    await ctx.channel.send(ctx.message.author.mention + " you are currently #" + str(q.queue.index(ctx.message.author) + 1) + " in line")

# Removes a given queue from the master list
@bot.command(
    help = "Deletes specified queue (Please do not abuse this) -- Default Input: \"Among Us\" -- Use: !delete <name> -- Other Names: !deleteq, !deleteque, !deletequeue, !delq, !delque, !delqueue",
    brief = "Deletes specified queue (Please do not abuse this) -- Default Input: \"Among Us\" -- Use: !delete <name> ",
    aliases = ['deleteq', 'deleteque', 'delq', 'delque', 'deletequeue']
)
async def delete(ctx, name="Among Us"):
    q = get_queue(name)
    if not q:
        await ctx.channel.send("Error: please enter a valid queue name to delete")
        return
    current_queues.remove(q)
    await ctx.channel.send("Deleted the {} queue".format(q.game))

# Print out all current queues (mostly for debugging)
@bot.command(
    help = "Prints out all active queues -- Use: !viewall -- Other Names: !viewqs, !viewques, !viewqueues, !printall, !printqs, !printques, !printqueue",
    brief = "Prints out all active queues -- Use: !viewall",
    aliases = ['viewqs', 'viewques', 'viewqueues', 'printall', 'printqs', 'printques', 'printqueues']
)
async def viewall(ctx):
    for Queue in current_queues:
        curr = Queue.print_queue()
        await ctx.channel.send(embed=curr)

bot.run(TOKEN)
