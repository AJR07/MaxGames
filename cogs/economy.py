import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import firebase_admin
from firebase_admin import firestore
from utils import check
import random
import math
import asyncio
import time
from discord_slash import SlashContext, cog_ext
import threading

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = firestore.client()
        self.initation = self.client.get_cog("Init")
        self.hidden = False



    # Curb gambling addiction
    @check.is_banned()
    @commands.command(name="coinflip", description="provide 2 arguments, the choice of your coin: head/tail, and the amount you want to bet", aliases= ["cf"], usage="coinflip <choice> <amount>")
    @cooldown(1, 8, BucketType.user)
    async def _coinflip(self, ctx, choice: str, amount: int = 1):
        self.initation = self.client.get_cog("Init")
        await self.initation.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        if doc.exists:
            dict1 = doc.to_dict()
            if dict1["money"] < amount:
                embed = discord.Embed(
                    title="Amount in bank too low",
                    description="The amount that you want to gamble is more than what you have in your bank.",
                    color=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)
                return
            if amount <= 0:
                doc_ref = self.db.collection("users").document(
                    "{}".format(str(ctx.author.id))
                )
                doc = doc_ref.get()
                if doc.exists:
                    dict1 = doc.to_dict()
                    dict1["money"] = -1
                    doc_ref.set(dict1)
                embed = discord.Embed(
                    title="Amount gambled unacceptable",
                    description="It appears that you have been attempting to exploit the system and this is very bad!!! Therefore, your balance will be set to negative 1.",
                    color=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)

            side = 0
            if choice == "head" or choice == "heads":
                side = 0
            elif choice == "tail" or choice == "tails":
                side = 1
            else:
                raise discord.ext.commands.errors.MissingRequiredArgument

            result = random.randint(0, 100) >= 40
            if result:
                embed = discord.Embed(
                    title="Coinflip results",
                    description=f"Welp, the coin flipped to **{'tails' if not side else 'heads'}**. You lost {amount} points to coinflipping :(",
                    colour=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)
                dict1["money"] -= amount
                # await ctx.send(f"Welp you lost {amount} points to coinflipping :(")
                ctx.send
            else:
                dict1["money"] += amount
                # await ctx.send(f"Oh wow, you won {amount} points to coinflipping :O")
                embed = discord.Embed(
                    title="Coinflip results",
                    description=f"Oh wow, the coin flipped to **{'tails' if side else 'heads'}**. You won {amount} points from the coin flip :O",
                    colour=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)
            doc_ref.set(dict1)
        else:
            await self.initation.init(ctx)

    @commands.command(
        name="gamble",
        description="Try to beat the computer at dice rolling. Keep rolling until you're happy :D",
        aliases=["g", "gg", "bet", "roll"],
        usage="gamble <amount>",
    )
    @cooldown(1, 8, BucketType.user)
    async def _gamble(self, ctx, amount: int = 5):
        self.initation = self.client.get_cog("Init")
        await self.initation.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        if doc.exists:
            dict1 = doc.to_dict()
            if dict1["money"] < amount:
                embed = discord.Embed(
                    title="Amount in bank too low",
                    description="The amount that you want to gamble is more than what you have in your bank.",
                    color=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)
                return
            if amount <= 0:
                doc_ref = self.db.collection("users").document(
                    "{}".format(str(ctx.author.id))
                )
                doc = doc_ref.get()
                if doc.exists:
                    dict1 = doc.to_dict()
                    dict1["money"] -= 0
                    if dict1["money"] < 0:
                        dict1["money"] = 0
                    doc_ref.set(dict1)
                embed = discord.Embed(
                    title="Amount gambled unacceptable",
                    description="It appears that you have been trying to exploit the system and this is very bad!!!",
                    color=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)
                return
            botnum = random.randint(1, 12)
            yournum = random.randint(1, 15)
            if yournum >= 13:
                yournum = random.randint(1, 6)
            if yournum > botnum:
                dict1["money"] += amount
                embed = discord.Embed(
                    title="Gambling results",
                    description="Bot rolled: "
                    + str(botnum)
                    + "\nYou rolled: "
                    + str(yournum)
                    + "\nYou won! Congrats. You now have "
                    + str(dict1["money"])
                    + " money",
                    colour=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )

                await ctx.reply(
                    embed=embed, allowed_mentions=discord.AllowedMentions.none()
                )
                doc_ref.set(dict1)
            elif yournum == botnum:
                dict1["money"] -= math.ceil(amount / 2)
                embed = discord.Embed(
                    title="Gambling results",
                    description="Bot rolled: "
                    + str(botnum)
                    + "\nYou rolled: "
                    + str(yournum)
                    + "\nYou drawed and lost half of your bet.\nYou now have "
                    + str(dict1["money"])
                    + " money.",
                    colour=0xFFFF00,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )

                await ctx.reply(
                    embed=embed, allowed_mentions=discord.AllowedMentions.none()
                )
                doc_ref.set(dict1)
            else:
                dict1["money"] -= amount
                embed = discord.Embed(
                    title="Gambling results",
                    description="Bot rolled: "
                    + str(botnum)
                    + "\nYou rolled: "
                    + str(yournum)
                    + "\nYou lost your whole bet.\nYou now have "
                    + str(dict1["money"])
                    + " money.",
                    colour=0xFF0000,
                )
                await ctx.reply(
                    embed=embed, allowed_mentions=discord.AllowedMentions.none()
                )
        else:
            await check.init(ctx)

    @check.is_banned()
    @commands.command(
        name="money",
        description="Allows you to get a source of unlimited points :O",
        usage="money",
        aliases=["m"],
    )
    @cooldown(1, 3, BucketType.user)
    async def _money(self, ctx):
        self.initation = self.client.get_cog("Init")
        await self.initation.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        if doc.exists:
            dict1 = doc.to_dict()
            dict1["money"] = dict1["money"] + 1
            doc_ref.set(dict1)
            embed = discord.Embed(
                title="Money added",
                description="Money has been added to your bank. ",
                colour=self.client.primary_colour,
            )
            embed.set_author(
                name=ctx.author.display_name,
                url="https://google.com",
                icon_url=ctx.author.avatar_url,
            )
            embed.add_field(name="New Balance", value=f'{dict1["money"]}', inline=True)
            embed.set_footer(
                text="Find our more about how to use other currency functions by typing 'm!help currency' :D"
            )
            await ctx.reply(
                embed=embed, allowed_mentions=discord.AllowedMentions.none()
            )
        else:
            await self.initation.init(ctx)
            # await ctx.send("Now you can start running currency commands :D")

    @check.is_banned()
    @commands.command(name="bal",
        description="Allows you to check your current balance",
        usage="bal",
        aliases=["balance", "b"],)
    @cooldown(1, 5, BucketType.user)
    async def bal(self, ctx):
        self.initation = self.client.get_cog("Init")
        await self.initation.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        if doc.exists:
            embed = discord.Embed(
                title="Current Amount",
                description="How much money do you have in your bank?",
                colour=self.client.primary_colour,
            )
            embed.set_author(
                name=ctx.author.display_name,
                url="https://google.com",
                icon_url=ctx.author.avatar_url,
            )
            embed.add_field(
                name="Balance", value=f'{doc.to_dict()["money"]}', inline=True
            )
            await ctx.reply(
                embed=embed, allowed_mentions=discord.AllowedMentions.none()
            )
        else:
            await self.initation.init(ctx)
            # return False

    @commands.command(
        name="leaderboard",
        description="Shows you the richest and most wealthy people in the server you are in :O",
        usage="leaderboard",
        aliases=["l", "rich", "r", " l"],
    )
    @cooldown(1, 10, BucketType.user)
    async def _leaderboard(self, ctx):
        self.initation = self.client.get_cog("Init")
        await self.initation.checkserver(ctx)

        doc_ref = self.db.collection("servers").document("{}".format(str(ctx.guild.id)))
        doc = doc_ref.get()
        dict2 = doc.to_dict()["users"]
        dict3 = {}
        for i in dict2.keys():
            doc_ref = self.db.collection("users").document("{}".format(i))
            doc = doc_ref.get()
            dict1 = doc.to_dict()
            if dict1 == None:
                continue
            dict3[i] = dict1["money"]
        description = ""
        count = 1
        for i in sorted(dict3.items(), key=lambda kv: (kv[1]), reverse=True):
            user = await self.client.fetch_user(int(i[0]))
            description += f"{count}) {user.mention} - {i[1]} points\n"
            count += 1
            if count > 10:
                break
        embed = discord.Embed(
            title=f"Leaderboard in {ctx.message.guild.name}:",
            description=description,
            colour=self.client.primary_colour,
        )
        embed.set_author(
            name="Hallo Bot",
            icon_url="https://cdn.discordapp.com/attachments/797393542251151380/839131666483511336/476ffc83637891f004e1ba6e1ca63e6c.jpg",
        )
        await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(
        name="hourly",
        description="Hourly points :D",
        usage="hourly",
        aliases=["h"],
    )
    @cooldown(1, 3600, BucketType.user)
    async def hourly(self, ctx):
        await self.initation.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        booster = 1
        if doc.exists:
            dict1 = doc.to_dict()
            # value = int(doc.to_dict()['money'])
            dict1["money"] = dict1["money"] + booster * (random.randint(20, 50))
            doc_ref.set(dict1)
            embed = discord.Embed(
                title="Hourly claimed :D",
                description="Money gained from saying hourly!",
                colour=self.client.primary_colour,
            )
            embed.set_author(
                name=ctx.author.display_name,
                url="https://google.com",
                icon_url=ctx.author.avatar_url,
            )
            embed.add_field(name="New Balance", value=f'{dict1["money"]}', inline=True)
            await ctx.reply(
                embed=embed, allowed_mentions=discord.AllowedMentions.none()
            )

    @commands.command(
        name="daily",
        description="Daily points :D",
        usage="daily",
        aliases=["d"],
    )
    @cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        await self.initation.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        booster = 1
        if doc.exists:
            dict1 = doc.to_dict()
            # value = int(doc.to_dict()['money'])
            dict1["money"] = dict1["money"] + booster * (random.randint(20, 200))
            doc_ref.set(dict1)
            embed = discord.Embed(
                title="Daily claimed :D",
                description="Daily money",
                colour=self.client.primary_colour,
            )
            embed.set_author(
                name=ctx.author.display_name,
                url="https://google.com",
                icon_url=ctx.author.avatar_url,
            )
            embed.add_field(name="New Balance", value=f'{dict1["money"]}', inline=True)
            await ctx.reply(
                embed=embed, allowed_mentions=discord.AllowedMentions.none()
            )

    @cog_ext.cog_slash(name="hour", description="Claim your hourly money here :D")
    async def _hourly_cog(self, ctx):
        await self._hourly(ctx)

    @check.is_staff()
    @commands.command(
        hidden=True,
    )
    async def _setmoney(self, ctx, amount: int, name: discord.Member = None):
        if name == None:
            uid = str(ctx.author.id)
        else:
            uid = str(name.id)

        doc_ref = self.db.collection("users").document("{}".format(uid))
        doc = doc_ref.get()
        if doc.exists:
            dict2 = doc.to_dict()
            dict2["money"] = amount
            doc_ref.set(dict2)
            embed = discord.Embed(
                title="User amount set",
                description=f"Amount of <@{uid}> has been set to {amount}.",
                colour=self.client.primary_colour,
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="User's account not initiated.",
                description="This user has not initiated an account. Please make sure that the person has used hallo bot before :D",
                color=self.client.primary_colour,
            )
            await ctx.send(embed=embed)
    @check.is_banned()
    @commands.command(
        name="seboost",
        description="Experimental function that boosts ur se luck :o",
        usage="seboost",
        aliases=["seb"] 
    )
    @cooldown(1,100,BucketType.user)
    async def seboost(self,ctx):
        self.init = self.client.get_cog("Init")
        await self.init.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        if doc.exists:
            dict1 = doc.to_dict()
            if dict1["money"] < 100:
                embed=discord.Embed(
                    title="You don't have enough money to boost your luck :(",
                    description="Come back when you have 100 :D",
                    color=0xff0000
                )
                await ctx.reply(embed=embed)
            else:
                embed=discord.Embed(
                    title="Yay! You boosted your se luck.",
                    description="",
                    color=self.client.primary_colour
                )
                await ctx.reply(embed=embed)
                dict1["money"] -= 100
                dict1["seboosted"] = True
                doc_ref.set(dict1)
                await asyncio.sleep(50)
                dict1["seboosted"] = False
                await ctx.author.send("Your se boost ended D:")
                doc_ref.set(dict1)
    @check.is_banned()
    @commands.command(
        name="snake eyes",
        description="A random dice game that everyone loves.",
        usage="snakeeyes",
        aliases=["se", "snakeyes"],
    )
    @cooldown(1, 10, BucketType.user)
    async def se(self, ctx, amount: int):
        self.init = self.client.get_cog("Init")
        await self.init.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        if doc.exists:
            dict1 = doc.to_dict()
            if dict1["money"] < amount:
                embed = discord.Embed(
                    title="Amount in bank too low",
                    description="The amount that you want to gamble is more than what you have in your bank.",
                    color=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)
                return
            if amount <= 0:
                doc_ref = self.db.collection("users").document(
                    "{}".format(str(ctx.author.id))
                )
                doc = doc_ref.get()
                if doc.exists:
                    dict1 = doc.to_dict()

                    doc_ref.set(dict1)
                embed = discord.Embed(
                    title="Amount gambled unacceptable",
                    description="It appears that you have been attempting to exploit the system and this is very bad!!! Stop doing this or we'll set your balance to 0.",
                    color=self.client.primary_colour,
                )
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                )
                await ctx.reply(embed=embed)
                return

            embed = discord.Embed(
                title="Rolling dice...",
                description=":game_die::game_die:",
                color=self.client.primary_colour,
            )

            messagec = await ctx.reply(embed=embed)
            await asyncio.sleep(2)
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            if dice1 != 1 and dice2 != 1:
                dict1["money"] -= amount
                nowmoney = dict1["money"]
                doc_ref.set(dict1)
                embed = discord.Embed(
                    title="You rolled " + str(dice1) + " and " + str(dice2) + "!",
                    description="You didn't get any snake eyes. Beeg sed. You now have "
                    + str(nowmoney)
                    + " money.",
                    color=0xFF0000,
                )
                if dict1["seboosted"]:
                    embed.add_field(
                        name="Snake eyes boost active",
                        value="This boost expires 50 seconds after activation",
                        inline=True
                    )
                await messagec.edit(embed=embed)
            elif dice1 == 1 and dice2 != 1:
                if dict1["seboosted"] == True:
                    earnt = math.floor(2.3*amount)
                else:
                    earnt = math.floor(1.8 * amount)
                dict1["money"] += earnt
                doc_ref.set(dict1)
                nowmoney = dict1["money"]
                embed = discord.Embed(
                    title="You rolled " + str(dice1) + " and " + str(dice2) + "!",
                    description="You got one snake eye! You won 1.8x your bet. You now have "
                    + str(nowmoney)
                    + " money.",
                    color=self.client.primary_colour,
                )
                if dict1["seboosted"]:
                    embed.add_field(
                        name="Snake eyes boost active",
                        value="This boost expires 50 seconds after activation",
                        inline=True
                    )
                await messagec.edit(embed=embed)
            elif dice1 != 1 and dice2 == 1:
                if dict1["seboosted"] == True:
                    earnt = math.floor(2.3*amount)
                else:
                    earnt = math.floor(1.8 * amount)
                dict1["money"] += earnt
                nowmoney = dict1["money"]
                doc_ref.set(dict1)
                embed = discord.Embed(
                    title="You rolled " + str(dice1) + " and " + str(dice2) + "!",
                    description="You got one snake eye! You won 1.8x your bet. You now have "
                    + str(nowmoney)
                    + " money.",
                    color=self.client.primary_colour,
                )
                if dict1["seboosted"]:
                    embed.add_field(
                        name="Snake eyes boost active",
                        value="This boost expires 50 seconds after activation",
                        inline=True
                    )
                await messagec.edit(embed=embed)
            else:
                if dict1["seboosted"] == True:
                    earnt = math.floor(12*amount)
                else:
                    earnt = math.floor(10 * amount)
                dict1["money"] += earnt
                nowmoney = dict1["money"]
                doc_ref.set(dict1)
                embed = discord.Embed(
                    title="You rolled " + str(dice1) + " and " + str(dice2) + "!",
                    description="You got two snake eyes! You won 10x your bet. You now have "
                    + str(nowmoney)
                    + " money. Woo!",
                    color=self.client.primary_colour,
                )
                if dict1["seboosted"]:
                    embed.add_field(
                        name="Snake eyes boost active",
                        value="This boost expires 50 seconds after activation",
                        inline=True
                    )
                await messagec.edit(embed=embed)
        else:
            await self.init.init(ctx)
    
    @commands.command(
        name="search",
        description="Look for stuff! Who knows what you might get.",
        usage="search",
        aliases=["scout","find"]
    )
    @cooldown(1,60,BucketType.user)
    async def search(self,ctx):
        num = random.randint(1,1000)
        self.init = self.client.get_cog("Init")
        await self.init.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        if doc.exists:
            dict1 = doc.to_dict()
            if num < 8:
                dict1["money"] = 0
                embed = discord.Embed(
                    title="You were so depressed at not being able to find anything that you died.",
                    description="You lost all your money!",
                    color=0xff0000
                )
                await ctx.reply(embed=embed)
            elif num < 190:
                dict1["money"] += 5
                embed=discord.Embed(
                    title="You found a 5 dollar note on the floor!",
                    description="Money +5",
                    color=self.client.primary_colour
                )
                await ctx.reply(embed=embed)
            elif num < 250:
                dict1["maxigamespins"] += 1
                randm = "in a mall!"
                if (random.randint(1,2) == 2):
                    randm="on the floor!"
                embed=discord.Embed(
                    title="You found a Maxigames pin " + randm,
                    description="View how many pins you have [idk, add to inventory?]",
                    color=self.client.primary_colour
                )
                await ctx.reply(embed=embed)
            elif num < 380:
                dict1["money"] += 10
                embed=discord.Embed(
                    title="You found a crumpled ten dollar bill on the floor!",
                    description="Money +10",
                    color=self.client.primary_colour
                )
                await ctx.reply(embed=embed)
                
            else:
                await ctx.reply("I need to code this...")
        doc_ref.set(dict1)
    @commands.command(
        name="lottery",
        description="Buy as many lottery tickets as you want :D",
        usage="lottery [num num num num num num] (6 distinct numbers between 1 and 35)",
        aliases=["raffle","lotto"]
    )
    @cooldown(1,60,BucketType.user)
    async def lottery(self,ctx,*msgg:int):
        msg = list(msgg)
        if len(msg) != 6:
            embed=discord.Embed(
                title="You didn't enter 6 arguments!",
                description="",
                color=0xff0000
            )
            await ctx.reply(embed=embed)
            return
        for i in msg:
            if int(i) > 35 or int(i) < 1:
                embed=discord.Embed(
                    title="Invalid option for lottery!",
                    description="Your guess " + str(i) + " was invalid\nYou need to input 6 space-separated integers between 1 and 35 :D",
                    color=0xff0000
                )
                await ctx.reply(embed=embed)
                return
        for i in range(6):
            for j in range(i+1,6):
                if msg[i] == msg[j]:
                    embed=discord.Embed(
                        title="You can't use the same number twice!",
                        description="",
                        color=0xff0000
                    )
                    await ctx.reply(embed=embed)
                    return
                    
        correct=[]
        count = 0
        curr = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
        for i in range(6):
            elem = random.choice(curr)
            correct.append(elem)
            curr.remove(elem)
        correct.sort()
        msg.sort()
        for i in range(6):
            for j in range(6):
                if msg[i] == correct[j]:
                    count += 1
        win = [0,2,6,24,100,500,5000]
        self.init = self.client.get_cog("Init")
        await self.init.checkserver(ctx)
        doc_ref = self.db.collection("users").document("{}".format(str(ctx.author.id)))
        doc = doc_ref.get()
        for i in range(6):
            msg[i] = str(msg[i])
            correct[i] = str(correct[i])
        if doc.exists:
            dict1 = doc.to_dict()
            if dict1["money"] < 10:
                embed=discord.Embed(
                    title="You don't have enough money! You need 10 money.",
                    description="",
                    color=0xff0000
                )
                await ctx.reply(embed=embed)
            
            if count == 0:
                dict1["money"] -= 10
                moneynow = dict1["money"]
                embed=discord.Embed(
                    title="You didn't get any numbers correct! You lost your bet and now have " + str(moneynow) + " money.",
                    description="Your guess was: " + " ".join(msg) + "\nThe correct guess was: " + " ".join(correct),
                    color=0xff0000
                )
                await ctx.reply(embed=embed)
            elif count == 1:
                dict1["money"] += 40
                moneynow = dict1["money"]
                embed=discord.Embed(
                    title="You got 1 number correct! You won 2x your bet! You now have " + str(moneynow) + " money.",
                    description="Your guess was: " + " ".join(msg) + "\nThe correct guess was: " + " ".join(correct),
                    color=0xffff00
                )
                await ctx.reply(embed=embed)
            else:
                dict1["money"] += win[count]
                moneynow = dict1["money"]
                embed=discord.Embed(
                    title="You got " + str(count) + " numbers correct! You won " + win[count] + "x your bet! You now have " + str(moneynow) + " money.",
                    description="Your guess was: " + " ".join(msg) + "\nThe correct guess was: " + " ".join(correct),
                    color=self.client.primary_colour
                )
                await ctx.reply(embed=embed)
        doc_ref.set(dict1)
def setup(client):
    client.add_cog(Economy(client))
