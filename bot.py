import discord
from discord.ext import commands
import yaml
import asyncio
import traceback
import os
import random
from io import BytesIO
import praw
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import aiohttp
from PIL import Image,ImageFilter
from async_timeout import timeout
bot = commands.Bot(command_prefix = commands.when_mentioned_or('.'))
bot.currentgames = []
bot.gamecount = 0
with open(r'data.yml') as file:
    tokend = yaml.load(file,Loader=yaml.FullLoader)
    bot.token = tokend['token']
    bot.secret = tokend['secret']
    bot.id = tokend['id']
    bot.username = tokend['username']
    bot.password = tokend['password']
    file.close()
async def getbyt(url):
    async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    byt = (await r.read())
                    return(byt)
                    #await imgf.close()
                else:
                    return False
                del r
def postmeme(title,byt):
    reddit = praw.Reddit(client_id = bot.id,
                         client_secret = bot.secret,
                         user_agent = bot.id,
                         username = bot.username,
                         password = bot.password)
    with Image.open(BytesIO(byt)) as img:
        size = img.size
        wmark = Image.open('watermark.png')
        wthf = wmark.resize((100,100),5)
        wthf.putalpha(64)
        y = size[1]-100
        img.paste(wthf,(0,y),wthf)
        img.save('meme.png')
        image = 'meme.png'
        sub = reddit.subreddit('MemeMixGame').submit_image(title,image,timeout=30.0)
        y = sub.permalink
        furls = f'https://www.reddit.com{y}'
        return(furls)
        os.remove('meme.png')
        

    

    


class MyHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)
class mememix(commands.Cog):
    """ The main and real game"""
    def __init__(self,bot):
        self.bot = bot
        self.mlist = None
        self.commandexec = False
        self.mixer = None
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    
    
    async def cog_after_invoke(self, ctx):
        print(self.mlist)
        mis = []
        for e in self.mlist:
            mis.append(e.id)

        print(self.commandexec)
        if self.commandexec:
            vlist = []
            votdict = {}
            votes = [0,0,0]
            def votecheck(reaction,user):
                print((reaction.message.id in mis) and not user.bot)
                return((reaction.message.id in mis) and not user.bot)
                
            try:
                async with timeout(1800.0):
                    while True:
                        try:
                            reaction,user = await self.bot.wait_for('reaction_add',timeout=2.0,check=votecheck)
                            if (str(reaction.emoji) in ['<:upvote:700689655607197746>','\U0000274e']):
                                if str(reaction.emoji) == '\U0000274e':
                                    if user.guild_permissions.manage_guild:
                                        embed = discord.Embed(title='Memix Results!')
                                        channel = self.bot.get_channel(710470130680987648)
                                        winndex = 0
                                        ma = -999999999999999999999999999999999999999999999
                                        for i in range(0,3):
                                            v = votes[i]
                                            if v> ma:
                                                ma = v
                                                winndex = i
                                            i+=1


                                        embed.description = (f'''
                                        Voting Results are out!
                                        Meme 1: {votes[0]}
                                        Meme 2: {votes[1]}
                                        Meme 3: {votes[2]}
                                        The winner is Meme {winndex+1}''')
                                        await channel.send(embed=embed)
                                        await channel.send(f'{self.mixer[winndex].mention} COngrats on the win')
                                        msg = await channel.fetch_message(mis[winndex])
                                        e = msg.embeds[0]
                                        url = (e.image.url)
                                        title = f"{self.mixer[winndex].display_name} 's Meme for MemeMix round {self.bot.gamecount}"
                                        async with ctx.typing():
                                            byt = await getbyt(url)
                                            ur = postmeme(title,byt)
                                            return await ctx.send(ur)
                                            break
                                    else:
                                        await reaction.message.remove_reaction(reaction,user)
                                elif str(reaction.emoji) == '<:upvote:700689655607197746>':
                                    if user not in vlist:
                                        v = mis.index(reaction.message.id)
                                        votes[v] = votes[v] + 1
                                        votdict.update({f'{user.name}':v})
                                        vlist.append(user)
                                        await user.send(f'Your vote for meme {v+1} has been recorded')
                                        await reaction.message.remove_reaction(reaction,user)
                                        print(votes)
                                    else:
                                        
                                        v = mis.index(reaction.message.id)
                                        votes[v] = votes[v] + 1
                                        ind = votdict[str(user.name)]
                                        votes[ind] = votes[ind] -1
                                        await user.send(f'Your vote for meme {v+1} has been recorded. We have removed yout vote for meme {ind+1}')
                                        await reaction.message.remove_reaction(reaction,user)
                                        print(votes)
                            else:
                                await reaction.message.remove_reaction(reaction,user)
                        except asyncio.TimeoutError:
                            continue
                        except asyncio.CancelledError:
                            continue

            except asyncio.TimeoutError:
                channel = self.bot.get_channel(710470130680987648)
                embed = discord.Embed(title='Memix Results!')
                winndex = 0
                ma = -999999999999999999999999999999999999999999999
                for i in range(0,3):
                    v = votes[i]
                    if v> ma:
                        ma = v
                        winndex = i
                    i+=1


                embed.description = (f'''
    Voting Results are out!
    Meme 1 {votes[0]}
    Meme 2: {votes[1]}
    Meme 3: {votes[2]}
    The winner is Meme {winndex+1}''')
                await channel.send(embed=embed)
                await channel.send(f'{self.mixer[winndex].mention} COngrats on the win')
                msg = await channel.fetch_message(mis[winndex])
                e = msg.embeds[0]
                url = str(e.image.url)
                title = f"{self.mixer[winndex].display_name} 's Meme for MemeMix round {self.bot.gamecount}"
                async with ctx.typing(): 
                    byt = await getbyt(url)
                    ur = postmeme(title,byt)
                    return await ctx.send(ur)
                
        else:
            print('Game was unsuccesful')
    @commands.command()
    @commands.is_owner()
    async def voting(self,ctx):
        """ tests the voting system (only the owner can run it) Please do not run this command"""
        channel = self.bot.get_channel(710470130680987648)
        self.mlist = []
        memeurllist = ['https://media.discordapp.net/attachments/711563666943639582/711897308836397076/un82ifsnvge31.png','https://media.discordapp.net/attachments/711889053192290305/711897237629698138/images_16.jpeg','https://media.discordapp.net/attachments/711556060376465478/711896804324802560/blurple.png']
        await ctx.send('All memes have been submitted')
        for i in range(0,3):
            embed = discord.Embed(title = f'Test has submitted his meme')
            embed.set_image(url=memeurllist[i])
            msg = await channel.send(embed=embed)
            self.mlist.append(msg)
            await msg.add_reaction('<:upvote:700689655607197746>')
        self.commandexec = True
                    
    @commands.command()
    @commands.max_concurrency(1,commands.BucketType.guild)
    async def creategame(self,ctx):
        self.mixer = []
        self.mlist = []
        """ Creates and runs a mememix game to play 
        
        Please not eyou require 3 players and a 30 mins to make the meme"""
        players = []
        await ctx.trigger_typing()
        players.append(ctx.author)
        msg = await ctx.send('React with the the plus to join the meme mixer!\n Only 3 people in a round')
        
        await msg.add_reaction('\U00002795')
        def recheck(reaction,user):
                return(user is not ctx.author
                    and reaction.message.channel == ctx.channel
                    and not user.bot
                    and reaction.message.id == msg.id
                    and user not in players)
        
        try:
            async with timeout(30):
                while True:
                    print(len(players))
                    if len(players) == 3:
                        break
                    else:
                        try:
                            reaction,user = await self.bot.wait_for('reaction_add',timeout=10.0,check=recheck)
                            players.append(user)
                            await ctx.send(f'User {user.mention} has joined, React with the \U00002795 to join the game,you still have time')
                        except(asyncio.TimeoutError):
                            continue
        except (asyncio.TimeoutError, asyncio.CancelledError):
            return await ctx.send(f'Meme Mixer requires 3 people including yourself. Please find {3-len(players)} more people to play with.\n {players[0].mention} The gamehas been cancelled. Create new one when you have enough people')
            
        else:
            def scrambled(orig):
                dest = orig[:]
                random.shuffle(dest)
                return dest         
            if len(players)  == 3:
                print('Game may begin')
                await ctx.send('Game has started, evaluating roles')
                
                memeurllist = []
                capt = []
                temp = []
                l = scrambled(players)
                self.mixer = l
                #mixer = 0,1,2
                #capt = 2,0,1
                #temp = 1,2,0
                capt = [l[2],l[0],l[1]]
                temp = [l[1],l[2],l[0]]
                

            else:

                return await ctx.send(f'Meme Mixer requires 3 people including yourself. Please find {3-len(players)} more people to play with')  
                
            def check(message,turns):
                return(
                    message.author == self.mixer[turns] and message.guild == None and not user.bot and (message.content.lower().startswith('submit') or message.content.lower().startswith('cancel') ))
            try:
                async with timeout(5400.0):
                    for turns in range(0,3):
                        c = capt[turns]
                        t = temp[turns]
                        m = self.mixer[turns]
                        embed = discord.Embed(title=f'Mixer Cycle {self.bot.gamecount+1}: Round {turns+1}')
                        embed.description = (f'''Caption: {c.mention}\nTemplate: {t.mention}\nMixer: {m.mention}\n Please send your captions and template to the Mixer.
Mixer, please DM your meme to the  <@711503516778233886> , me. Please make sure to use the keyword `submit` while submitting.''')
                        await ctx.send(f'{c.mention},{t.mention},{m.mention}',embed=embed)
                        try:
                            async with timeout(1800.0):
                                while True:
                                    try:
                                        msg = await self.bot.wait_for('message',timeout=600.00)
                                        r = check(msg,turns)
                                        print(r)
                                        if r:
                                            if len(msg.attachments) != 0:
                                                try:
                                                    image_url = msg.attachments[0].url
                                                    memeurllist.append(image_url)
                                                    await self.mixer[turns].send('Recieved your submission!')
                                                    embed = discord.Embed(title = f'{self.mixer[turns].display_name} has submitted their meme')
                                                    embed.set_image(url=image_url)
                                                    await ctx.send(embed=embed)
                                                    break
                                                except:
                                                    await self.mixer[turns].send('I was unable to use the attachment you provided')
                                                    continue
                                            else:
                                                await self.mixer[turns].send('Hey do send the meme asap')
                                                continue
                                            
                                    except asyncio.TimeoutError:
                                        continue
                        except asyncio.TimeoutError:
                            return await ctx.send(f'{self.mixer[turns].mention}You did not submit a meme. So the game was cancelled')
                            break
                        turns+=1

                    
            except asyncio.TimeoutError:
                return await ctx.send('Mixer cancelled')
            else:
                peopleuvoted = []
                channel = self.bot.get_channel(710470130680987648)

                
                await ctx.send('All memes have been submitted')
                await channel.send(f'Memeix Cycle {self.bot.gamecount+1}')
                for i in range(0,3):
                    embed = discord.Embed(title = f'{self.mixer[i].mention} has submitted their meme')
                    embed.set_image(url=memeurllist[i])
                    msg = await channel.send(embed=embed)
                    self.mlist.append(msg)
                    await msg.add_reaction('<:upvote:700689655607197746>')
                self.commandexec = True
                self.bot.gamecount+=1    

@bot.event
async def on_ready():
    bot.add_cog(mememix(bot))
    print('Bit is onlibe')
@bot.command()
async def testcustomemoji(ctx):
    msg = await ctx.send('will try adding the Uv to this')
    await msg.add_reaction('<:upvote:700689655607197746>')
@bot.command()
@commands.is_owner()
async def upload(ctx,text:str='Optional'):
    async with ctx.typing():
        if len(ctx.message.attachments ) != 0:
        
                try:
                    image_url = ctx.message.attachments[0].url
                    
                except:
                    return await ctx.send('I was unable to use the attachment you provided')
        elif text != 'Optional':
            validate = URLValidator()
            try:
                validate(text)
            except ValidationError:
                return await ctx.send('Your Url is invalid')
            else:
                image_url = str(text)
        print(image_url)
        byt = await getbyt(image_url)
        ur = postmeme(byt)
        return await ctx.send(ur)

@bot.event
async def on_command_error(ctx,error):
    ers = (f'{error}')
    etype = type(error)
    trace = error.__traceback__

    # the verbosity is how large of a traceback to make
    # more specifically, it's the amount of levels up the traceback goes from the exception source
    verbosity = 4

    # 'traceback' is the stdlib module, `import traceback`.
    lines = traceback.format_exception(etype, error, trace, verbosity)

    # format_exception returns a list with line breaks embedded in the lines, so let's just stitch the elements together
    traceback_text = ''.join(lines)

    # now we can send it to the user
    if isinstance(error,commands.MaxConcurrencyReached):
        times = error.number
        cat = error.per
        return await ctx.send( 'There is aldready a mixer game in play, please wait for this one to end')
    elif isinstance(error,commands.CommandNotFound):
        return await ctx.send('That command does not exist')
    else:
        print(traceback_text)
        name = ctx.author.display_name
        server = ctx.guild.name
        embed = discord.Embed(title='MIXER UNKOWN ERROR OCCURED',description=f'```python\n{error}\n ```\nThe command {ctx.invoked_with} caused the error\n**Author:**{name}\n**Server:**{server}',color=ctx.guild.me.color)
        embed.add_field(name='SENT', value="Your error has been sent to my creator's bug channel")
        nemb =  discord.Embed(title='MIXER UNKOWN ERROR OCCURED',description=f'```python\n{traceback_text}\n ```\nThe command {ctx.invoked_with} caused the error\n**Author:**{name}\n**Server:**{server}',color=ctx.guild.me.color)
        channel = bot.get_channel(711925873435213846)
        await channel.send(embed=nemb)
        await ctx.send(embed=embed)


                    
        








bot.run(bot.token)