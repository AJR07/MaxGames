import asyncio
from typing import List, Optional, Union

import discord
from discord import embeds
from discord.ext import commands

from discord_components import Button, ButtonStyle, InteractionType

import copy

#creds https://github.com/khk4912/EZPaginator/blob/master/EZPaginator/EZPaginator.py
class Paginator:
    def __init__(
        self, 
        client: Union[
            discord.Client,
            discord.AutoShardedClient,
            commands.Bot,
            commands.AutoShardedBot,
        ], 
        ctx: commands.Context,
        message: discord.Message, 
        pages: List[discord.Embed], 
        buttons: List[List[Button]] = [[]],
        previous_symbol: str = "⬅️ Previous",
        next_symbol: str = "Next ➡️",
        timeout: int = 60,
        start_page:int = 0
    ):
        self.client = client
        self.ctx = ctx
        self.message = message
        self.pages = pages
        self.buttons: List[List[Button]] = buttons
        self.previous_symbol = previous_symbol
        self.next_symbol = next_symbol
        self.timeout = timeout
        self.page_num = start_page

        if (not(
            isinstance(client, discord.Client)
            or isinstance(client, discord.AutoShardedClient)
            or isinstance(client, commands.Bot)
            or isinstance(client, commands.AutoShardedBot))
        ):
            raise TypeError("Paginator client must be a discord.Client or commands.Bot")
        # print("values initiated")
    
    async def start(self):
        add_on_buttons: List[Button] = [Button(style=ButtonStyle.green, label=self.previous_symbol, disabled=True), Button(style=ButtonStyle.green, label=self.next_symbol)]
        component = copy.copy(self.buttons)
        component[0] = add_on_buttons + component[0]
        
        # print(component)
        components = [add_on_buttons]
        await self.message.edit(
            embed=self.pages[self.page_num],
            components=copy.copy(component)
        )

        def check(interation):
            return interation.message == self.message and self.ctx.author == interation.user
            
        while True:
            try:
                res = await self.client.wait_for("button_click", timeout = self.timeout, check = check)
                # print(res)
                await res.respond(
                    type=InteractionType.DeferredUpdateMessage # , content=f"{res.component.label} pressed"
                )

                if res.component.label == self.previous_symbol:
                    self.page_num -= 1
                    if self.page_num <= 0:
                        self.page_num=0
                        add_on_buttons = [Button(style=ButtonStyle.green, label=self.previous_symbol, disabled=True), Button(style=ButtonStyle.green, label=self.next_symbol)]

                        component = copy.copy(self.buttons)
                        component[0] = add_on_buttons + component[0]
                        
                        # print(component)
                        components = [add_on_buttons]
                        await self.message.edit(
                            embed=self.pages[self.page_num],
                            components=copy.copy(component)
                        )
                    else:
                        add_on_buttons = [Button(style=ButtonStyle.green, label=self.previous_symbol), Button(style=ButtonStyle.green, label=self.next_symbol)]
                        ccomponent = copy.copy(self.buttons)
                        component[0] = add_on_buttons + component[0]
                        
                        # print(component)
                        components = [add_on_buttons]
                        await self.message.edit(
                            embed=self.pages[self.page_num],
                            components=copy.copy(component)
                        )
                elif res.component.label == self.next_symbol:
                    self.page_num += 1
                    if self.page_num >= len(self.pages)-1:
                        self.page_num = len(self.pages)-1
                        add_on_buttons = [Button(style=ButtonStyle.green, label=self.previous_symbol), Button(style=ButtonStyle.green, label=self.next_symbol, disabled=True)]
                        component = copy.copy(self.buttons)
                        component[0] = add_on_buttons + component[0]
                        
                        # print(component)
                        components = [add_on_buttons]
                        await self.message.edit(
                            embed=self.pages[self.page_num],
                            components=copy.copy(component)
                        )
                    else:

                        add_on_buttons = [Button(style=ButtonStyle.green, label=self.previous_symbol), Button(style=ButtonStyle.green, label=self.next_symbol)] + self.buttons[0]
                        component = copy.copy(self.buttons)
                        component[0] = add_on_buttons + component[0]
                        
                        # print(component)
                        components = [add_on_buttons]
                        await self.message.edit(
                            embed=self.pages[self.page_num],
                            components=copy.copy(component)
                        )

            except asyncio.TimeoutError:
                # print("Times up")
                component = copy.copy(self.buttons)
                if component != [[]]:
                    await self.message.edit(
                        embed=self.pages[self.page_num],
                        components=copy.copy(component)
                    )
                else:
                    await self.message.delete()
                return
            