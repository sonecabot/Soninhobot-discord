
import discord
from discord.ext import commands
import os

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')

@bot.command()
async def ping(ctx):
    """Comando básico de teste"""
    await ctx.send('Pong!')

@bot.command()
async def ola(ctx):
    """Comando de saudação"""
    await ctx.send(f'Olá, {ctx.author.mention}!')

@bot.command()
async def info(ctx):
    """Informações do servidor"""
    embed = discord.Embed(title="Informações do Servidor", color=0x00ff00)
    embed.add_field(name="Nome", value=ctx.guild.name, inline=True)
    embed.add_field(name="Membros", value=ctx.guild.member_count, inline=True)
    await ctx.send(embed=embed)

# Adicione seu token do bot aqui
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("ERRO: Token do Discord não encontrado!")
    print("Adicione seu token nas variáveis de ambiente como DISCORD_TOKEN")
else:
    bot.run(TOKEN)
