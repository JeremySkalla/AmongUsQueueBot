import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

# Globals
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
current_servers = []

bot = commands.Bot(command_prefix=".")  # Sets up bot

# ----------------------------------------
#             Queue Class
# ----------------------------------------

class Server:
    def __init__(self, ctx):
        self.guild = ctx.guild
        self.name = ctx.guild.name
        self.queues = []

        current_servers.append(self)

class Queue:
    # Initialization
    def __init__(self, name, ctx):
        # Default to 10-player queue for everything
        self.max = 10
        # Create queue for game
        self.game = name
        self.queue = []

        server = None
        for s in current_servers:
            if ctx.guild == s.guild:
                server = s
                break
        
        server.queues.append(self)

    # Mutators
    def set_max(self, new_max):
        self.max = new_max

    def set_num(self, new_num):
        self.num = new_num

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
            text="Use .queue {} to join the queue.".format(self.game))

        return embed

# ----------------------------------------
#            Helper Functions
# ----------------------------------------

def get_server(ctx):
    for s in current_servers:
        if ctx.guild == s.guild:
            return s
    return False

def get_queue(name, server):
    for Queue in server.queues:
        if Queue.game == name:
            return Queue
    return False


def get_players_queue(player, server):
    for Queue in server.queues:
        if player in Queue.queue:
            return Queue
    return False

# ----------------------------------------
#               On Ready
# ----------------------------------------

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="use .help"))

# ----------------------------------------
#              Bot Commands
# ----------------------------------------

# Queue function
@bot.command(
    help = "Adds player to queue and prints out the current queue -- Use: .queue -- Other Names: .q, .que, .queue, .joinqueue, .cue",
    brief = "Adds player to queue and prints out the current queue",
    aliases = ['q', 'que', 'joinqueue', 'cue', 'quwu']
)
async def queue(ctx, name="Among Us"):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    # If the queue doesn't exist, create one
    q = get_queue(name, server)
    if not q:
        q = Queue(name, ctx)

    # Check if the person is in the queue already
    if ctx.message.author in q.queue:
        await ctx.channel.send(ctx.message.author.mention + " you are already in queue. use .leave to remove yourself")
        return

    # Normal behavior
    q.queue.append(ctx.message.author)
    await ctx.channel.send(ctx.message.author.mention + ", you are #" + str(len(q.queue)) + " in the queue")
    e = q.print_queue()
    await ctx.send(embed=e)
    
    # If we have enough for a new lobby
    if len(q.queue) == q.max:
        t = "The queue has enough players for a new lobby!"
        d = "Please join if you are mentioned here!"
        c = discord.Color.teal()

        players = ""
        num_spots = q.max
        while num_spots > 0:
            player = q.queue.pop(0)
            players += player.mention + " "
            num_spots -= 1

        e = discord.Embed(title=t, description=d, color=c)

        await ctx.channel.send(embed=e)
        await ctx.channel.send(players)

# Removes player from queue if they don't want to play
@bot.command(
    help = "Removes player from queue -- Default Input: \"Among Us\" -- Use: .unqueue <name> -- Other Names: .unq, .unque, .leave, .leaveq, .leaveque, .leavequeue, .dq, .deq, .deque, .dequeue",
    brief = "Removes player from queue",
    aliases = ['unq', 'unque', 'leave', 'leaveq', 'leaveque', 'leavequeue', 'dq', 'deq', 'deque', 'dequeue', 'unquwu', 'dequwu']
)
async def unqueue(ctx, name="Among Us"):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    # If the queue doesn't exist, create one
    q = get_queue(name, server)
    if not q:
        await ctx.channel.send("Queue {} does not exist".format(q.game))
        return

    if ctx.message.author not in q.queue:
        await ctx.channel.send(ctx.message.author.mention + " you are currently not in that queue. Use .queue to join Among Us queue, or .queue <Name> to join another")
        return

    q.queue.remove(ctx.message.author)
    await ctx.channel.send(ctx.message.author.mention + " you have been removed from the {} queue".format(q.game))
        
    e = q.print_queue()
    await ctx.send(embed=e)
    
# If the lobby needs more players, pings players in queue when spots are open
@bot.command(
    help = "Pings players in queue when spots are open -- Default Input: NONE -- Use: .ping <num> <name> -- Other Names: .ping, .pingplayer, .need, .needplayer",
    brief = "Pings players in queue when spots are open",
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
            if arg2:
                if arg2.isdigit():
                    await ctx.channel.send("Error: cannot have two ints")
                    return
                else:
                    num_spots = int(arg1)
                    name = arg2
            # Arg2 is auto among us
            else:
                num_spots = int(arg1)
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

    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    # If the queue doesn't exist, create one
    q = get_queue(name, server)
    if not q:
        q = Queue(name, ctx)

    if len(q.queue) == 0:
        e = discord.Embed(title="There are no players to ping. Sorry!")
        await ctx.channel.send(embed=e)
        return

    # If we get here, we have a valid queue with at least one player
    if num_spots == 1:
        t = "The lobby has 1 open spot!"
    else:
        t = "The lobby has " + str(num_spots) + " open spots!"

    d = "Please join if you are mentioned here!"
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
    help = "Prints out the queue with its name -- Default Input: \"Among Us\" -- Use: .view <game> -- Other Names: .view, .viewq, .viewqueue, .print, .printq, .printqueue",
    brief = "Prints out the queue with its name",
    aliases = ['print', 'printq', 'printqueue', 'viewq', 'viewqueue'])
async def view(ctx, name="Among Us"):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    # If the queue doesn't exist, create one
    q = get_queue(name, server)
    if not q:
        await ctx.channel.send("Error: Please enter a valid queue name to view!")

    e = q.print_queue()
    await ctx.channel.send(embed=e)

# Displays # of users in queue
@bot.command(
    help = "Displays # of users in queue -- Default Input: \"Among Us\" -- Use: .length <name> -- Other Names: .qlength, .quelength, .queuelength",
    brief = "Displays # of users in queue",
    aliases = ['qlength', 'quelength', 'queuelength']
)
async def length(ctx, name="Among Us"):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    # If the queue doesn't exist, create one
    q = get_queue(name, server)
    if not q:
        await ctx.channel.send("Error: Please enter a valid queue to view length")
        return

    await ctx.channel.send("There are " + str(len(q.queue)) + " players in queue")

# Checks how many players are ahead of user
@bot.command(
    help = "Displays how many players are ahead of user -- Use: .spot -- Other Names: .spotinq, .spotinque, .spotinqueue, .place, .placeinq, .placeinque, .placeinqueue",
    brief = "Displays how many players are ahead of user",
    aliases = ['spotinq', 'spotinque', 'spotinqueue', 'place', 'placeinq', 'placeinque', 'placeinqueue']
)
async def spot(ctx):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    q = get_players_queue(ctx.message.author, server)
    if not q:
        await ctx.channel.send(ctx.message.author.mention + " you are currently not in any queue. Use .queue to join Among Us queue, or .queue <Name> to join another")
        return

    await ctx.channel.send(ctx.message.author.mention + " you are currently #" + str(q.queue.index(ctx.message.author) + 1) + " in line")

# Removes a given queue from the master list
@bot.command(
    help = "Deletes specified queue (Please do not abuse this) -- Default Input: \"Among Us\" -- Use: .delete <name> -- Other Names: .del, .deleteq, .deleteque, .deletequeue, .delq, .delque, .delqueue",
    brief = "Deletes specified queue (Please do not abuse this)",
    aliases = ['del', 'deleteq', 'deleteque', 'delq', 'delque', 'deletequeue']
)
async def delete(ctx, name="Among Us"):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    q = get_queue(name, server)
    if not q:
        await ctx.channel.send("Error: please enter a valid queue name to delete")
        return
    server.queues.remove(q)
    await ctx.channel.send("Deleted the {} queue".format(q.game))

# Print out all current queues (mostly for debugging)
@bot.command(
    help = "Prints out all active queues -- Use: .viewall -- Other Names: .viewqs, .viewques, .viewqueues, .printall, .printqs, .printques, .printqueue",
    brief = "Prints out all active queues",
    aliases = ['viewqs', 'viewques', 'viewqueues', 'printall', 'printqs', 'printques', 'printqueues']
)
async def viewall(ctx):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    for Queue in server.queues:
        curr = Queue.print_queue()
        await ctx.channel.send(embed=curr)

@bot.command(
    help = "Sets the max for a specified queue -- Default Input: \"Among Us\" -- Use: .setmax <max> <name> -- Other Names: .max, .newmax, .setqmax, .setqmax, .setquemax, .setqueuemax",
    brief = "Sets the max for a specified queue",
    aliases = ['max', 'newmax', 'setqmax', 'setquemax', 'setqueuemax']
)
async def setmax(ctx, max, name='Among Us'):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    q = get_queue(name, server)
    if not q:
        await ctx.channel.send("Error: Enter a valid queue name to delete!")
        return
    
    if max.isdigit():
        if int(max) <= 0:
            await ctx.channel.send("Error: Enter a valid maximum for the queue")
        else:
            q.set_max(int(max))
            await ctx.channel.send("{0} queue has been set to a max of {1}".format(q.game, max))
    else:
        ctx.channel.send("Error: Elease enter a valid max!")

@bot.command(
    help = "Removes player from a queue -- Default Input: .remove <name> -- Use: ",
    brief = "Removes player from a queue",
    aliases = ['removeplayer', '']
)
async def remove(ctx, player, name='Among Us'):
    server = get_server(ctx)
    if not server:
        server = Server(ctx)

    q = get_queue(name, server)
    if not q:
        await ctx.channel.send("Error: Enter a valid queue to delete the player from!")
        return

    # can't use "in" because queue is player object not name
    for p in q.queue:
        if p.name.lower() == player.lower():
            q.queue.remove(p)
            e = q.print_queue()
            await ctx.send(embed=e)
            return

    await ctx.channel.send("Error: Enter a valid player to delete from the queue!")

# Runs the bot
bot.run(TOKEN)