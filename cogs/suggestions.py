import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import os
from utils import check
from firebase_admin import firestore
import asyncio


class Suggestions(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.hidden = False
        self.db = firestore.client()

    @check.is_banned()

    @commands.command(
        name="suggest",
        description="Suggest anything that you want us to know about!!! Be it a game that you really want to be implemented, or some comments you have on what can be improved :D",
        usage="suggest <suggestion>",
        aliases=["sug", "suggestadd","suggestion"],
    )
    @cooldown(1,60,BucketType.user)
    async def suggest(self, ctx, *msg):
        suggestion = " ".join(msg[:])
        channel = self.client.get_channel(865821669730156544)
        embed = discord.Embed(
            title="New Suggestion",
            description=f"{ctx.author.mention} has submitted a suggestion.",
            colour=self.client.primary_colour,
        )
        embed.add_field(name="Suggestion", value=suggestion, inline=False)
        message = await channel.send(embed=embed)

        acknowledgement = discord.Embed(
            title="Suggestion Submitted",
            description=f"Your suggestion has been submitted. Thank you for your suggestion.",
            colour=self.client.primary_colour,
        )
        await ctx.reply(embed=acknowledgement)

        def is_admin(uid):
            doc_ref = self.db.collection(u"admin").document(u"{}".format("authorised"))
            doc = doc_ref.get()
            people = doc.to_dict()
            allowed = people["owner"] + people["staff"]
            if str(uid) not in allowed:
                return False
            else:
                return True

        def check(reaction, user):
            return (
                (user == ctx.author or is_admin(user.id))and reaction.message == message and reaction.emoji == "❌"
            )

        await message.add_reaction("⬆️")
        await message.add_reaction("⬇️")
        await message.add_reaction("❌")
        await message.add_reaction("✅")

        reaction, user = await self.client.wait_for("reaction_add", check=check)
        await message.delete()

        delete_channel = self.client.get_channel(866339642075775058)
        await delete_channel.send(embed=embed)

    @check.is_banned()
    @commands.command(
        name="bugreport",
        description="Report bugs!",
        usage="bugreport <suggestion>",
        aliases=["report", "br", "bug"],
    )
    async def report(self, ctx, *msg):
        suggestion = " ".join(msg[:])
        channel = self.client.get_channel(869960880631218196)
        embed = discord.Embed(
            title="New Bug",
            description=f"{ctx.author.mention} has submitted a bug.",
            colour=self.client.primary_colour,
        )
        embed.add_field(name="Suggestion", value=suggestion, inline=False)
        message = await channel.send(embed=embed)

        acknowledgement = discord.Embed(
            title="Bug report submitted",
            description=f"Your report has been submitted. Thank you for notifying us of this bug, we will private message you once its fixed/dealt with!",
            colour=self.client.primary_colour,
        )
        await ctx.reply(embed=acknowledgement)

        def check(reaction, user):
            return (
                user == ctx.author
                and reaction.message == message
                and reaction.emoji == "❌"
            )
        await message.add_reaction("❌")
        reaction, user = await self.client.wait_for("reaction_add", check=check)
        await message.delete()

        toDelete = await channel.send("You have 1 minute to write a message to the user that submitted this bug report!")
        toDelete2 = 0
        messageToUser = "Fixed!"
        def check(message):
            return message.author == ctx.author
        try: 
            newMessage = await self.client.wait_for(
                "message", timeout=60, check=check
            )
            toDelete2 = await newMessage.reply("Messaged received, sending reply")
            messageToUser = newMessage.content
            await newMessage.delete()
        except asyncio.TimeoutError:
            toDelete2 = await ctx.reply("1 minute is up, sending default message")
        
        await toDelete.delete()
        await ctx.author.send(embed = discord.Embed(title="Bug Report Fixed!", description = f"Your bug report about {suggestion} has been fixed! The developer's reply: `{messageToUser}`"))
        await toDelete2.delete()
        


def setup(client):
    client.add_cog(Suggestions(client))
