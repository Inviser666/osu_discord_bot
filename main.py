from typing import assert_type

from scoreToImg import makeScoreImage
import discord
from discord.ext import commands
from config import settings
import asyncio
import ossapi
from ossapi import mod, Ossapi
from ossapi.enums import Grade
import os
import asyncio
import requests
from numpy import round
from array import array
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = settings['prefix'],intents = intents)
bot.status = discord.Status.do_not_disturb

#List of processing users
user_list = []
#List of processing channels
channel_list = array('i')
#Костылище ебаное
isResumed = False
#Osu keys
id = settings['osuid']
key = settings['osukey']
api = Ossapi(id,key)

#Amount of processing scores
limit_of_scores = 100

def addNewUser(userID):
    newuser = {
        'userid': "",
        'pp': 0,
        'last_list' : []
    }
    newuser['userid'] = userID
    newuser['last_list'] = []
    if len(user_list) != 0:
        for user in user_list:
            if (user['userid'] == userID):
                return False
    user_list.append(newuser.copy())
    return True

def initUsers():
    del user_list[:]
    file = open("playersid.txt", "r")
    while (True):
        line = file.readline()
        print(line)
        if not line:
            break
        addNewUser(line)
    file.close()

def initChannels():
    del channel_list[:]
    file = open("channels.txt", "r")
    while (True):
        line = file.readline()
        print(line)
        if not line:
            break
        channel_list.append(int(line.rstrip()))
    file.close()

def init():
    initUsers()
    initChannels()

def rewriteUsers():
    file = open("playersid.txt", "w")
    for user in user_list:
        file.write(user['userid'])
    file.close()

def addToFile(newUserID):
    file = open("playersid.txt","a")
    file.write(str(newUserID) + "\n")
    file.close()

@bot.hybrid_command()
async def dog(ctx: commands.Context):
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    Pic_link = response.json()["message"]
    await ctx.send(Pic_link)

@bot.command(name="cat")
async def Cat(ctx):
    response = requests.get("https://api.thecatapi.com/v1/images/search")
    Pic_link = response.json()[0]["url"]
    await ctx.send(Pic_link)

async def sendAllChannels(message : str):
    if len(channel_list) != 0:
        for channel in channel_list:
            channel = bot.get_channel(int(channel))
            if isinstance(channel, discord.TextChannel):
                await channel.send(message)

@bot.hybrid_command(name="start", description="start sending scores in this chat")
async def plus(ctx):
    addNewChannel(ctx.channel.id)

@bot.hybrid_command(name="stop", description="stop sending scores in this chat")
async def minus(ctx):
    removeChannel(ctx.channel.id)

def addNewChannel(channelID):
    logfile = open('channels.txt', 'r')
    channels = logfile.readlines()
    logfile.close()
    found = False
    for line in channels:
        if str(channelID) in line:
            print("Found it")
            found = True
    if not found:
        channel_list.append(int(channelID))
        logfile = open('channels.txt', 'a')
        logfile.write(str(channelID)+"\n")
        logfile.close()

def removeChannel(channelID):
    with open("channels.txt", "r") as f:
        lines = f.readlines()
        f.close()
    with open("channels.txt", "w") as f:
        for line in lines:
            if line.strip("\n") != str(channelID):
                f.write(line)
            else:
                channel_list.remove(int(line))
        f.close()

@bot.event
async def on_ready():
    await bot.tree.sync()
    init()
    print("Бот готов!")
    await start()

@bot.hybrid_command(name="ping")
async def ping1(ctx):
    print(ctx.channel.id)
    #await Guild.get_channel('1201434939267227690')
    await ctx.send('pong')

@bot.hybrid_command(description="начать отслеживать скоры игрока")
@discord.app_commands.describe(username="юзернейм в осу")
async def add(ctx: commands.Context, username: str):
    msg : str
    user : ossapi.User
    try:
        user = api.user(username)
    except:
        print(str(username) + " не найден")
        return False
    
    isNew = addNewUser(user.id)
    if(isNew):
        addToFile(user.id)
        msg = str(user.username) + " добавлен"
    else:
        msg = str(user.username) + " уже существует в списке"

    print(msg)
    await ctx.channel.send(msg)

@bot.hybrid_command(description="начать отслеживать скоры игрока по id")
@discord.app_commands.describe(user_id="id юзера")
async def addid(ctx, user_id):
    string : str
    user : ossapi.User
    try:
        user = api.user(user_id)
    except:
        string = str(user_id) + " не найден"
        print(string)
        return False
    
    isNew = addNewUser(user.id)
    if(isNew):
        addToFile(user.id)
        string = str(user.username) + " добавлен"
        print(string)
        await ctx.channel.send(string)
    else:
        string = str(user.username) + " уже существует в списке"
        print(string)
        await ctx.channel.send(string)

@bot.hybrid_command(name="remove", description="перестать отслеживать скоры игрока")
@discord.app_commands.describe(username="юзернейм в осу")
async def removePlayer(ctx: commands.Context, username: str):
    isHere = False
    with open("playersid.txt", "r") as f:
        lines = f.readlines()
        f.close()
    with open("playersid.txt", "w") as f:
        for line in lines:
            if line.strip("\n") != str(username):
                f.write(line)
            else:
                isHere = True
                for user in user_list:
                    if user['userid'] == int(line):
                        user_list.remove(user)
                string = str(api.user(username).username) + " удален"
                print(string)
                await ctx.channel.send(string)
        if not isHere:
            string = str(api.user(username).username) + " не найден в списке"
            print(string)
            await ctx.channel.send(string)
        f.close()

@bot.hybrid_command(description="отслеживаемые игроки")
async def players(ctx):
    file = open("playersid.txt", "r")
    string = ''
    i = 0
    while (True):
        line : str
        line = file.readline()
        print(line)
        if not line:
            if(i == 0):
                file.close()
                await ctx.channel.send("Нет игроков в списке")
                return
            break
        string = string +"(id: " + line.rstrip() + ") " + str(api.user(str(line.rstrip())).username) + "\n";
        i += 1
    await ctx.channel.send(string)
    file.close()

@bot.hybrid_command(description="кролик")
async def rabbit(ctx: commands.Context):
    await ctx.send(random.choice(list(open('rabbits.txt'))))

@bot.event
async def on_resumed():
   pass

@bot.hybrid_command(name="rs", description="последний скор игрока")
@discord.app_commands.describe(username="юзернейм в осу")
# TODO: юзернейм сделать typing.Optional[str], когда будет возможность сохранять id дискорда
async def resentScore(ctx: commands.Context, username: str):
    u_id:ossapi.User
    try:
        u_id = api.user(username)
    except:
        print('Нет такого юзера')
        return
    score = api.user_scores(u_id,"recent",include_fails=True,mode="osu",limit=1,offset=0)[0]

    weightpp =str(0)
    pp = str(0)
    if score.weight is None:
        pass
    else:
        weightpp= str(score.weight.pp)
        pp = str(round(score.weight.pp/(score.weight.percentage/100),2))

    if score.rank == Grade.F:
        score.rank = Grade.D

    if score.beatmapset is ossapi.BeatmapsetCompact and score.beatmap is ossapi.Beatmap:
        strResult= "Игрок " + score.user().username+" получил "+pp+"pp "+"на карте "+score.beatmapset.title+" от "+score.beatmapset.artist+" Дифа: "+score.beatmap.version+" с точностью "+str(round(score.accuracy*100,2))+"%. Моды:"+mod.ModCombination.short_name(score.mods)+". Взвешено: " + weightpp + "pp.";
        strImage = makeScoreImage(str(score.beatmap.id),str(score.user().username),str(score.created_at.date()) + " " + str(score.created_at.time()),str(score.mods.value),score.score,score.max_combo,str(score.rank).replace('Grade.',''),str(score.statistics.count_50),str(score.statistics.count_100),str(score.statistics.count_300),str(score.statistics.count_miss),str(score.statistics.count_katu),str(score.statistics.count_geki),pp)
        embed = discord.Embed(
            title="score",
            color=discord.Color.random(),
            description=strResult
        )
        embed.set_image(url=strImage)
        await ctx.send(embed=embed)

async def start():
    user_iterator = 0
    while True:
        await startIteration(user_iterator)
        user_iterator += 1
        if(user_iterator == len(user_list)):
            user_iterator = 0
        await asyncio.sleep(2)
        

async def startIteration(user_iterator):
    try:
        score_list = api.user_scores(user_list[user_iterator]['userid'],"best",include_fails=False,mode="osu",limit=limit_of_scores,offset=0)
    except:
        return
    

    my_score_list = score_list
    
    if(len((user_list[user_iterator])['last_list']) != len(my_score_list) ):
        user_list[user_iterator]['last_list'] = my_score_list
    else:
        i = 0
        isNewScore = False
        for score in my_score_list:
            if(score.id != user_list[user_iterator]['last_list'][i].id):
                print(score)
                if score.weight is ossapi.Weight and score.beatmapset is ossapi.BeatmapsetCompact and score.beatmap is ossapi.Beatmap:
                    strResult = "Игрок " + score.user().username+" получил "+str(round(score.weight.pp/(score.weight.percentage/100),2))+"pp на карте "+score.beatmapset.title+" от "+score.beatmapset.artist+" Дифа: "+score.beatmap.version+" с точностью "+str(round(score.accuracy*100,2))+"%. Моды:"+mod.ModCombination.short_name(score.mods)+ ". Это его топ "+str(i+1)+" скор!"+"Взвешено: " + str(round(score.weight.pp,2)) + "pp.";
                    strImage = makeScoreImage(str(score.beatmap.id),str(score.user().username),str(score.created_at.date()) + " " + str(score.created_at.time()),str(score.mods.value),score.score,score.max_combo,str(score.rank).replace('Grade.',''),str(score.statistics.count_50),str(score.statistics.count_100),str(score.statistics.count_300),str(score.statistics.count_miss),str(score.statistics.count_katu),str(score.statistics.count_geki),str(round(score.weight.pp/(score.weight.percentage/100),2)))
                    user_list[user_iterator]['last_list'] = my_score_list
                    isNewScore = True
                    await sendAllChannels(strResult)
                    await sendAllChannels(strImage)
                break
            i += 1
    


bot.run(settings['token']) # Обращаемся к словарю settings с ключом token, для получения токенаd
