import discord
import os
import asyncio
import g4f
from g4f.client import Client
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("GPTBOT_TOKEN")

with open('ai_prompt.txt', 'r') as f:
    SYS_PROMPT = f.read()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='.', case_insensitive=True)
bot.help_command = None
inv_args = "&permissions=412317240384&scope=applications.commands%20bot"

client = Client()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('with you'), status=discord.Status.online)
    print(f'Logged in/Rejoined as {bot.user} (ID: {bot.user.id})')
    print(f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}{inv_args}")
    print('------ Error Log ------')


@bot.event
async def setup_hook():
    print('loading slash commands...')
    try:
        await bot.tree.sync(guild=None)
        pass
    except Exception as e:
        print(e)
    print("If you are seeing this then unseeyou's epic bot is working!")


@bot.command(name="chat", help="Chat with unseeAI")
async def on_message(ctx: commands.Context, *, message: str):
    loading_gif = "https://media1.tenor.com/m/ibuZFLK9qf8AAAAC/palia-loading.gif"
    icon_url = "https://cdn.discordapp.com/avatars/650923352097292299/b844503d610abb2d9e9ab3fce059cad8.webp"

    embed = discord.Embed(title="Generating Response...",
                          colour=discord.Colour.from_rgb(18, 114, 92),
                          description=f"**User Prompt**: {message}\n**Current Task:** generating chat history")
    embed.set_image(url=loading_gif)
    embed.set_footer(text="made by unseeyou | powered by gpt4free", icon_url=icon_url)

    msg = await ctx.reply(embed=embed, silent=True, mention_author=False)
    try:
        history = [m async for m in ctx.channel.history(limit=50)]
        history = history[1:]
        history.reverse()
        # print("Grabbed history")
        message_history = [{"role": "system",
                            "content": SYS_PROMPT}]
        for m in history:
            if (m.author.id == bot.user.id and
                    len([i for i in m.embeds if "unseeyou's epic website" not in i.description
                                                and "Traceback" not in i.description]) > 0):

                message_history.append({"role": "assistant",
                                        "content": m.embeds[0].description.split("**Response:** ")[1]
                                        if m.embeds[0].description.split("**Response:** ")[1] is not None else ""})
            elif m.content.startswith('.chat'):
                message_history.append({"role": "user",
                                        "content": m.content.replace("<@1083187041715625995>", "unseeAI")
                                       .replace(loading_gif, "[hidden response]")
                                       .replace(".chat ", "")})
            else:
                # ignore the messages which are not supposed to be seen by the bot"
                pass

        embed = discord.Embed(title="Generating Response...",
                              colour=discord.Colour.from_rgb(18, 114, 92),
                              description=f"**User Prompt**: {message}\n**Current Task:** generating AI response")
        embed.set_image(url=loading_gif)
        embed.set_footer(text="made by unseeyou | powered by gpt4free", icon_url=icon_url)
        await msg.edit(embed=embed)
        # print("Created message history, sending request...")
        # print(message_history)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=message_history
        )
        result_message = response.choices[0].message.content
        # print(f"Got response: {result_message}")
        embed = discord.Embed(title="Generating Response... DONE",
                              colour=discord.Colour.from_rgb(18, 114, 92),
                              description=f"**User Prompt**: {message}\n \n**Response:** {result_message}")
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text="made by unseeyou | powered by gpt4free", icon_url=icon_url)
        await msg.edit(embed=embed)

    except Exception as e:
        embed = discord.Embed(title="Generating Response... ERROR",
                              colour=discord.Colour.brand_red(),
                              description=f"**Traceback:** {str(e.with_traceback(e.__traceback__))[-4000:]}")
        embed.set_thumbnail(url="https://c.tenor.com/KGRLk_Dfub0AAAAC/scooby-doo-woof.gif")
        embed.set_footer(text="made by unseeyou | powered by gpt4free", icon_url=icon_url)
        await msg.edit(embed=embed)


@bot.hybrid_command(help='probably my ping')
async def ping(ctx: commands.Context):
    latency = round(bot.latency * 1000, 2)
    message = await ctx.send("Pong!")
    await message.edit(content=f"Pong! My ping is `{latency} ms`")
    # print(f'Ping: `{latency} ms`')


async def main():
    async with bot:
        await bot.start(TOKEN)


asyncio.run(main())
