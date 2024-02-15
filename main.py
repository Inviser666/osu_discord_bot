from scoreToImg import makeScoreImage
import discord
from discord.ext import commands
from config import settings
import asyncio
import time
from ossapi import Ossapi
from ossapi import mod
import os
import asyncio
from ossapi import OssapiAsync
import requests
from numpy import round
import sys

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = settings['prefix'],intents = intents)

#List of processing users
user_list = []
#List of processing channels
channel_list = []
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
    user_list.clear()
    file = open("playersid.txt", "r")
    while (True):
        line : str
        line = file.readline()
        print(line)
        if not line:
            break
        addNewUser(line)
    file.close()

def initChannels():
    channel_list.clear()
    file = open("channels.txt", "r")
    while (True):
        line : str
        line = file.readline()
        print(line)
        if not line:
            break
        channel_list.append(int(line.strip("\n")))
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

@bot.command(name="dog")
async def Dog(ctx):
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
            await bot.get_channel(channel).send(message)

@bot.command(name="test")
async def send(ctx):
    await sendAllChannels('qwerty')

@bot.command(name="start")
async def plus(ctx):
    addNewChannel(ctx.channel.id)

@bot.command(name="stop")
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
    init()
    print("Бот готов!")
    string = 'Я включился, встречайте!'
    #string = string + 'Я включился, встречайте! ' + 'https://cdn.discordapp.com/emojis/1139812673454886942.gif?size=48&name=hi&quality=lossless';
    
    #await sendAllChannels(string)
    #await sendAllChannels('https://cdn.discordapp.com/emojis/1139812673454886942.gif?size=48&name=hi&quality=lossless')
    await start()

@bot.command(name="ping")
async def ping1(ctx):
    print(ctx.channel.id)
    #await Guild.get_channel('1201434939267227690')
    await ctx.send('pong')

@bot.command()
async def add(ctx,arg):
    string : str
    user : str
    try:
        user = api.user(arg)
    except:
        string = str(arg) + " не найден"
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

@bot.command()
async def addid(ctx,arg):
    string : str
    user : str
    try:
        user = api.user(arg)
    except:
        string = str(arg) + " не найден"
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

@bot.command(name="remove")
async def removePlayer(ctx,arg):
    isHere = False
    with open("playersid.txt", "r") as f:
        lines = f.readlines()
        f.close()
    with open("playersid.txt", "w") as f:
        for line in lines:
            if line.strip("\n") != str(arg):
                f.write(line)
            else:
                isHere = True
                for user in user_list:
                    if user['userid'] == int(line):
                        user_list.remove(user)
                string = str(api.user(arg).username) + " удален"
                print(string)
                await ctx.channel.send(string)
        if not isHere:
            string = str(api.user(arg).username) + " не найден в списке"
            print(string)
            await ctx.channel.send(string)
        f.close()

@bot.command()
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

@bot.event
async def on_resumed():
   pass

@bot.command(name="rs")
async def resentScore(ctx,arg):
    u_id = 0
    try:
        u_id = api.user(arg)
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

    if score.rank == 'Grade.F':
        score.rank = 'Grade.D'

    strResult = "Игрок " + str(score._user.username)+" получил "+pp+"pp "+"на карте "+score.beatmapset.title+" от "+score.beatmapset.artist+" Дифа: "+score.beatmap.version+" с точностью "+str(round(score.accuracy*100,2))+"%. Моды:"+mod.ModCombination.short_name(score.mods)+". Взвешено: " + weightpp + "pp.";
    strImage = makeScoreImage(str(score.beatmap.id),str(score._user.username),str(score.created_at.date()) + " " + str(score.created_at.time()),str(score.mods.value),score.score,score.max_combo,str(score.rank).replace('Grade.',''),str(score.statistics.count_50),str(score.statistics.count_100),str(score.statistics.count_300),str(score.statistics.count_miss),str(score.statistics.count_katu),str(score.statistics.count_geki),pp)

    await sendAllChannels(strResult)
    await sendAllChannels(strImage)

async def start():
    user_iterator = 0
    while True:
        await startIteration(user_iterator)
        user_iterator += 1
        if(user_iterator == len(user_list)):
            user_iterator = 0
        await asyncio.sleep(2)
        

@bot.command(name="error")
async def error(ctx):
  os.system("main.py")


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
                #await ctx.channel.send(score)
                strResult = "Игрок " + str(score._user.username)+" получил "+str(round(score.weight.pp/(score.weight.percentage/100),2))+"pp "+"на карте "+score.beatmapset.title+" от "+score.beatmapset.artist+" Дифа: "+score.beatmap.version+" с точностью "+str(round(score.accuracy*100,2))+"%. Моды:"+mod.ModCombination.short_name(score.mods)+ ". Это его топ "+str(i+1)+" скор!"+"Взвешено: " + str(round(score.weight.pp,2)) + "pp.";
                strImage = makeScoreImage(str(score.beatmap.id),str(score._user.username),str(score.created_at.date()) + " " + str(score.created_at.time()),str(score.mods.value),score.score,score.max_combo,str(score.rank).replace('Grade.',''),str(score.statistics.count_50),str(score.statistics.count_100),str(score.statistics.count_300),str(score.statistics.count_miss),str(score.statistics.count_katu),str(score.statistics.count_geki),str(round(score.weight.pp/(score.weight.percentage/100),2)))
                #await ctx.channel.send(strResult)
                user_list[user_iterator]['last_list'] = my_score_list
                isNewScore = True
                await sendAllChannels(strResult)
                await sendAllChannels(strImage)
                break
            i += 1
        print(isNewScore)
    


bot.run(settings['token']) # Обращаемся к словарю settings с ключом token, для получения токенаd