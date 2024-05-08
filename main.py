import discord
import os
import asyncio
from g4f.client import Client
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("GPTBOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='.', case_insensitive=True)
bot.help_command = None

client = Client()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('with your mind'), status=discord.Status.online)
    print(f'Logged in/Rejoined as {bot.user} (ID: {bot.user.id})')
    print(
        f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=412317240384&scope=applications.commands%20bot")
    print('------ Error Log ------')


@bot.event
async def setup_hook():
    print('loading slash commands...')
    try:
        # await bot.tree.sync(guild=None)
        pass
    except Exception as e:
        print(e)
    print("If you are seeing this then unseeyou's epic bot is working!")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.channel.id in (1237592678368149564, 1237635305494941786):
        try:
            await message.add_reaction("💭")
            msg = await message.reply("https://tenor.com/view/palia-loading-palia-loading-waiting-forever-gif-9924694518018189823")
            history = [m async for m in message.channel.history(limit=31)]
            history = history[1:]
            history.reverse()
            print("Grabbed history")
            message_history = []
            message_history.append({"role": "system",
                                    "content": "you are a discord bot called unseeAI that is powered by AI, you can chat with anyone on the server. you were made by unseeyou, and whenever someone asks, link them to his website: https://unseeyou.pages.dev"})
            for m in history:
                if m.author.global_name == bot.user.global_name:
                    message_history.append({"role": "assistant", "content": m.content})
                else:
                    message_history.append({"role": "user", "content": m.content.replace("<@1083187041715625995>", "unseeAI")})
            print("Created message history")
            print(message_history)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message_history
            )
            result_message = response.choices[0].message.content
            print(f"Got response: {result_message}")
            await msg.edit(content=result_message)
            await message.add_reaction("✅")

        except Exception as e:
            await message.channel.send(f'Error: {e}')

    await bot.process_commands(message)


@bot.hybrid_command(help='probably my ping')
async def ping(ctx: commands.Context):
    latency = round(bot.latency * 1000, 2)
    message = await ctx.send("Pong!")
    await message.edit(content=f"Pong! My ping is `{latency} ms`")
    print(f'Ping: `{latency} ms`')


async def main():
    async with bot:
        await bot.start(TOKEN)


asyncio.run(main())
