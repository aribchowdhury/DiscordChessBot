import discord
from discord.ext.commands import Bot
from logic import ChessGame
import uuid
import io

bot = Bot(command_prefix="c!")
TOKEN = "OTM5OTU2NTMwMjEwNTM3NTUy.YgAYvA.-wKa0uqGsYKQdoIvngqLNj8LEB8"
current_games = {} # game_hash: Game
users_busy_playing = {} # userA: (userB, game_hash), userB: (userA, game_hash)
challenges_in_progress = set() # sorted[(userA, userB)]

@bot.event
async def on_ready():
	print(f"Bot connected as {bot.user}")
	await bot.change_presence(activity = discord.Activity(
							type = discord.ActivityType.playing, 
							name = 'Snake and Ladders'))
	
@bot.event
async def on_message(ctx):
	await bot.process_commands(ctx)
 
async def turnResults(ctx, arg1: str, arg2: str):
    res, ext = current_games[users_busy_playing[ctx.author][1]].move(ctx.author, arg1, arg2)
    if res == -1:
        await ctx.channel.send("Invalid move selected or in check. Use of command: c!mv arg1 arg2")
        return
    elif res == 1:
        with io.BytesIO() as image_binary:
            current_games[users_busy_playing[ctx.author][1]].drawBoard().save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(file=discord.File(fp=image_binary, filename='chessState.png'))
        await ctx.channel.send(f"{users_busy_playing[ctx.author][0].mention}")
    elif res == 5:
        await ctx.channel.send(f"{ext.mention} has been checkmated. The winner is {ctx.author.mention}")
    elif res == 3:
        await ctx.channel.send(f"{ext.mention} and {ctx.author.mention}'s game has resulted in a draw.")
    elif res == 4:
        await ctx.channel.send(f"{ext.mention} is in check.")
    if res == 5 or res == 3:
        current_games.pop(users_busy_playing[ctx.author][1])
        users_busy_playing.pop(users_busy_playing[ctx.author][0])
        users_busy_playing.pop(ctx.author)
    # Reactionary message for promotion of piece if necessary, check for checkmate after update afterwards

@bot.command(name="mv")
async def movePiece(ctx, arg1: str, arg2: str):
    if ctx.author not in users_busy_playing:
        await ctx.channel.send("Go start a game first!")
        return
    if len(arg1) != 2 or len(arg2) != 2 or not('a' <= arg1[0].lower() <= 'h') or not('a' <= arg2[0].lower() <= 'h') or\
    not('1' <= arg1[1] <= '8') or not('1' <= arg2[1] <= '8'):
        await ctx.channel.send("Invalid arguments selected. Use of command: c!mv arg1 arg2")
        return
    await turnResults(ctx, arg1, arg2)

@bot.command(name="mv castle")
async def castle(ctx, arg1, arg2): #king, queen
    if ctx.author not in users_busy_playing:
        await ctx.channel.send("Go start a game first!")
        return
    if len(arg1) != 2 or len(arg2) != 2 or not('a' <= arg1[0].lower() <= 'h') or not('a' <= arg2[0].lower() <= 'h') or\
    not('1' <= arg1[1] <= '8') or not('1' <= arg2[1] <= '8'):
        await ctx.channel.send("Invalid arguments selected. Use of command: c!castle king/queenPos rookPos")
        return 
    await turnResults(ctx, arg1, arg2)

@bot.command(name="mv enpassante")
# have to keep track of last move opponent made for this
async def enpassante(ctx, arg1, arg2):
    pass

@bot.command(name="retire")
async def retireGame(ctx):
    if ctx.author not in users_busy_playing:
        await ctx.channel.send("Go start a game first!")
        return
    await ctx.channel.send(f"Player {ctx.author.mention} has forfeited. The winner of the game is {users_busy_playing[ctx.author][0].mention}")
    current_games.pop(users_busy_playing[ctx.author][1])
    users_busy_playing.pop(users_busy_playing[ctx.author][0])
    users_busy_playing.pop(ctx.author)

@bot.command(name="play")
async def playGame(ctx, arg1 : discord.Member = None):
    if arg1 in users_busy_playing:
        await ctx.channel.send(f"{arg1} is busy playing with someone else. Wait your turn.")
        return
    challenges_in_progress.add((ctx.author, arg1))
    challenges_in_progress.add((arg1, ctx.author))
    await ctx.channel.send(f"{ctx.author.mention} has graciously invited you, {arg1.mention}, to play. \"c!accept {ctx.author.mention}\" to accept their challenge.")

@bot.command(name="accept")
async def acceptGame(ctx, arg1 : discord.Member = None):
    if ctx.author in users_busy_playing:
        await ctx.channel.send(f"Finish you current game first.")
        return
    if arg1 in users_busy_playing:
        await ctx.channel.send(f"{arg1} is busy playing with someone else. Wait your turn.")
        return
    if (ctx.author, arg1) in challenges_in_progress or (arg1, ctx.author) in challenges_in_progress:
        challenges_in_progress.discard((ctx.author, arg1))
        challenges_in_progress.discard((arg1, ctx.author))
        hash = str(uuid.uuid4())
        users_busy_playing[ctx.author] = (arg1, hash)
        users_busy_playing[arg1] = (ctx.author, hash)
        current_games[users_busy_playing[ctx.author][1]] = ChessGame(ctx.author,users_busy_playing[ctx.author][0])
        await ctx.channel.send(f"{arg1.mention}, {ctx.author.mention} has accepted the challenge.")
        await ctx.channel.send(f"{current_games[users_busy_playing[ctx.author][1]].mentionable_users[0].mention}")
        with io.BytesIO() as image_binary:
            current_games[users_busy_playing[ctx.author][1]].drawBoard().save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(file=discord.File(fp=image_binary, filename='chessState.png'))
    else:
        await ctx.channel.send(f"{ctx.author.mention} is trying to play a game with someone who didn't want to play with them.")

@bot.command(name="refresh")
async def refresh(ctx):
    print(current_games[users_busy_playing[ctx.author][1]].board)
    with io.BytesIO() as image_binary:
        current_games[users_busy_playing[ctx.author][1]].drawBoard().save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.channel.send(file=discord.File(fp=image_binary, filename='chessState.png'))
bot.run(TOKEN)