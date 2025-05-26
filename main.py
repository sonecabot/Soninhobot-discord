"""
Bot Discord completo inspirado em YAGPDB.xyz com comandos slash

Recursos:
- Comandos slash (/)
- Comando para limpar mensagens (limpar)
- Comando para lembrar (lembrar)
- Melhor tratamento de erros e mensagens feedback
- Logging básico

Configuração:
1. Instale Python 3.8+ e pacotes: discord.py, python-dotenv, asyncio
2. Crie .env com o token do bot (DISCORD_TOKEN)
3. Execute python bot.py

"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
import asyncio
from dotenv import load_dotenv
import logging
import requests
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuração intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='*', intents=intents, help_command=None)

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('yagpdb-like-bot')

# Evento ao iniciar o bot
@bot.event
async def on_ready():
    logger.info(f'Bot online! Logado como {bot.user} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Use /ajuda para comandos"))
    print(f'Bot online! Logado como {bot.user} (ID: {bot.user.id})')
    
    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        logger.info(f'Sincronizados {len(synced)} comandos slash globalmente')
        print(f'Sincronizados {len(synced)} comandos slash globalmente')
        
        # Sincronização específica para cada servidor (mais rápida)
        for guild in bot.guilds:
            try:
                await bot.tree.sync(guild=guild)
                logger.info(f'Comandos sincronizados para o servidor: {guild.name}')
                print(f'Comandos sincronizados para o servidor: {guild.name}')
            except Exception as e:
                logger.error(f'Erro ao sincronizar no servidor {guild.name}: {e}')
    except Exception as e:
        logger.error(f'Falha ao sincronizar comandos: {e}')

# Boas-vindas
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f'Bem-vindo(a) {member.mention}! Leia as regras e aproveite! :tada:')

# Comando ajuda
@bot.tree.command(name='ajuda', description='Mostra os comandos disponíveis')
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Ajuda - Comandos do Bot", color=0x5865F2)
    embed.description = "Comandos slash disponíveis:"
    embed.add_field(name='/ajuda', value='Mostra esta mensagem de ajuda', inline=False)
    embed.add_field(name='/ping', value='Verifica latência do bot', inline=False)
    embed.add_field(name='/piada', value='Conta uma piada de programação', inline=False)
    embed.add_field(name='/info-servidor', value='Informações do servidor', inline=False)
    embed.add_field(name='/info-usuario', value='Informações do usuário', inline=False)
    embed.add_field(name='/expulsar', value='Expulsa um usuário (perm. necessária)', inline=False)
    embed.add_field(name='/banir', value='Bane um usuário (perm. necessária)', inline=False)
    embed.add_field(name='/silenciar', value='Silencia um usuário (perm. necessária)', inline=False)
    embed.add_field(name='/limpar', value='Limpa mensagens no canal (perm. necessária)', inline=False)
    embed.add_field(name='/lembrar', value='Cria um lembrete', inline=False)
    embed.add_field(name='**Comandos Bíblicos (com prefixo *):**', value='Use `*ajuda biblia` para ver comandos bíblicos', inline=False)
    embed.set_footer(text='Inspirado em YAGPDB.xyz')
    await interaction.response.send_message(embed=embed)

# Ping
@bot.tree.command(name='ping', description='Verifica a latência do bot')
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f'Pong! Latência: {latency}ms')

# Piada
@bot.tree.command(name='piada', description='Conta uma piada de programação')
async def joke(interaction: discord.Interaction):
    jokes = [
        'Por que os programadores preferem o modo escuro? Porque a luz atrai bugs! 🐛',
        'Uma consulta SQL entra em um bar e pergunta: "Posso me juntar a vocês?"',
        'Por que desenvolvedores Java usam óculos? Porque não veem sharp.',
        'Quantos programadores para trocar uma lâmpada? Nenhum, é problema de hardware.',
        'Existem 10 tipos de pessoas: as que entendem binário e as que não.',
    ]
    await interaction.response.send_message(random.choice(jokes))

# Info servidor
@bot.tree.command(name='info-servidor', description='Mostra informações do servidor')
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"{g.name} - Informações do servidor", color=0x5865F2)
    embed.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
    embed.add_field(name="ID", value=str(g.id), inline=True)
    embed.add_field(name="Dono", value=str(g.owner), inline=True)
    embed.add_field(name="Membros", value=str(g.member_count), inline=True)
    embed.add_field(name="Criado em", value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="Nível de boost", value=str(g.premium_tier), inline=True)
    await interaction.response.send_message(embed=embed)

# Info usuário
@bot.tree.command(name='info-usuario', description='Mostra informações de um usuário')
@app_commands.describe(membro='O usuário para ver informações (opcional)')
async def userinfo(interaction: discord.Interaction, membro: discord.Member = None):
    member = membro or interaction.user
    embed = discord.Embed(title=f"{member}", color=0x5865F2)
    embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else discord.Embed.Empty)
    embed.add_field(name="ID", value=str(member.id), inline=True)
    embed.add_field(name="Entrou em", value=f"<t:{int(member.joined_at.timestamp())}:D>", inline=True)
    embed.add_field(name="Conta criada em", value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="Bot?", value="Sim" if member.bot else "Não", inline=True)
    await interaction.response.send_message(embed=embed)

# Expulsar
@bot.tree.command(name='expulsar', description='Expulsa um usuário do servidor')
@app_commands.describe(
    membro='O usuário para expulsar',
    motivo='Motivo da expulsão (opcional)'
)
async def kick(interaction: discord.Interaction, membro: discord.Member, motivo: str = None):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message('Você não tem permissão para expulsar membros.', ephemeral=True)
        return
    
    if membro == interaction.user:
        await interaction.response.send_message('Você não pode se expulsar.', ephemeral=True)
        return
    
    if not membro.kickable:
        await interaction.response.send_message('Não posso expulsar esse usuário.', ephemeral=True)
        return
    
    try:
        await membro.kick(reason=motivo)
        await interaction.response.send_message(f'Usuário {membro} expulso. Motivo: {motivo or "Nenhum fornecido"}')
    except Exception as e:
        await interaction.response.send_message('Falha ao expulsar usuário.', ephemeral=True)
        logger.error(e)

# Banir
@bot.tree.command(name='banir', description='Bane um usuário do servidor')
@app_commands.describe(
    membro='O usuário para banir',
    motivo='Motivo do banimento (opcional)'
)
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str = None):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message('Você não tem permissão para banir membros.', ephemeral=True)
        return
    
    if membro == interaction.user:
        await interaction.response.send_message('Você não pode se banir.', ephemeral=True)
        return
    
    if not membro.bannable:
        await interaction.response.send_message('Não posso banir esse usuário.', ephemeral=True)
        return
    
    try:
        await membro.ban(reason=motivo)
        await interaction.response.send_message(f'Usuário {membro} banido. Motivo: {motivo or "Nenhum fornecido"}')
    except Exception as e:
        await interaction.response.send_message('Falha ao banir usuário.', ephemeral=True)
        logger.error(e)

# Silenciar
@bot.tree.command(name='silenciar', description='Silencia um usuário')
@app_commands.describe(
    membro='O usuário para silenciar',
    motivo='Motivo do silenciamento (opcional)'
)
async def mute(interaction: discord.Interaction, membro: discord.Member, motivo: str = None):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message('Você não tem permissão para gerenciar cargos.', ephemeral=True)
        return
    
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="Muted")
    
    if role is None:
        try:
            role = await guild.create_role(name="Muted",
                                           color=discord.Color.dark_gray(),
                                           reason="Criado cargo 'Muted' para silenciar")
            for channel in guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False, add_reactions=False)
        except Exception as e:
            await interaction.response.send_message('Falha ao criar cargo Muted.', ephemeral=True)
            logger.error(e)
            return
    
    if role in membro.roles:
        await interaction.response.send_message('Este usuário já está silenciado.', ephemeral=True)
        return
    
    try:
        await membro.add_roles(role, reason=motivo)
        await interaction.response.send_message(f'Usuário {membro} silenciado. Motivo: {motivo or "Nenhum fornecido"}')
    except Exception as e:
        await interaction.response.send_message('Falha ao silenciar usuário.', ephemeral=True)
        logger.error(e)

# Limpar mensagens
@bot.tree.command(name='limpar', description='Limpa mensagens do canal')
@app_commands.describe(quantidade='Número de mensagens para apagar (1-100)')
async def clear(interaction: discord.Interaction, quantidade: int = 5):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message('Você não tem permissão para gerenciar mensagens.', ephemeral=True)
        return
    
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message("Por favor, informe um número entre 1 e 100.", ephemeral=True)
        return
    
    await interaction.response.defer()
    deleted = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f'{len(deleted)} mensagens apagadas.', ephemeral=True)

# Lembrar
@bot.tree.command(name='lembrar', description='Cria um lembrete')
@app_commands.describe(
    minutos='Tempo em minutos para o lembrete',
    mensagem='Mensagem do lembrete'
)
async def remind(interaction: discord.Interaction, minutos: int, mensagem: str):
    if minutos <= 0:
        await interaction.response.send_message('O tempo deve ser positivo.', ephemeral=True)
        return
    
    await interaction.response.send_message(f'Ok! Vou te lembrar em {minutos} minuto(s). ⏰')
    await asyncio.sleep(minutos*60)
    await interaction.followup.send(f'{interaction.user.mention}, lembrete: {mensagem}')

# ===== COMANDOS BÍBLICOS COM PREFIXO =====

# Função para buscar versículo na API
async def buscar_versiculo(livro, capitulo, versiculo):
    try:
        url = f"https://www.abibliadigital.com.br/api/verses/nvi/{livro}/{capitulo}/{versiculo}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar versículo: {e}")
        return None

# Função para buscar versículo aleatório
async def buscar_versiculo_aleatorio():
    try:
        url = "https://www.abibliadigital.com.br/api/verses/nvi/random"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar versículo aleatório: {e}")
        return None

# Comando para pesquisar versículo específico
@bot.command(name='versiculo')
async def versiculo_comando(ctx, livro: str, capitulo: int, versiculo: int, canal: discord.TextChannel = None):
    """
    Busca um versículo específico da Bíblia
    Uso: *versiculo joão 3 16 [#canal]
    """
    canal_destino = canal or ctx.channel
    
    # Verificar se tem permissão para enviar no canal especificado
    if canal and not canal.permissions_for(ctx.author).send_messages:
        await ctx.send("❌ Você não tem permissão para enviar mensagens nesse canal.", delete_after=10)
        return
    
    await ctx.send("🔍 Buscando versículo...")
    
    dados = await buscar_versiculo(livro.lower(), capitulo, versiculo)
    
    if dados:
        embed = discord.Embed(
            title=f"📖 {dados['book']['name']} {dados['chapter']}:{dados['number']}",
            description=dados['text'],
            color=0x4A90E2
        )
        embed.add_field(name="Versão", value="NVI (Nova Versão Internacional)", inline=False)
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await canal_destino.send(embed=embed)
        
        if canal != ctx.channel:
            await ctx.send(f"✅ Versículo enviado para {canal.mention}")
    else:
        await ctx.send("❌ Versículo não encontrado. Verifique se o livro, capítulo e versículo estão corretos.")

# Comando para versículo diário
@bot.command(name='versiculo diario')
async def versiculo_diario(ctx, canal: discord.TextChannel = None):
    """
    Envia um versículo aleatório do dia
    Uso: *versiculo diario [#canal]
    """
    canal_destino = canal or ctx.channel
    
    # Verificar se tem permissão para enviar no canal especificado
    if canal and not canal.permissions_for(ctx.author).send_messages:
        await ctx.send("❌ Você não tem permissão para enviar mensagens nesse canal.", delete_after=10)
        return
    
    await ctx.send("🙏 Buscando versículo do dia...")
    
    dados = await buscar_versiculo_aleatorio()
    
    if dados:
        embed = discord.Embed(
            title=f"🌅 Versículo do Dia - {dados['book']['name']} {dados['chapter']}:{dados['number']}",
            description=dados['text'],
            color=0xFFD700
        )
        embed.add_field(name="Versão", value="NVI (Nova Versão Internacional)", inline=False)
        embed.set_footer(text=f"Versículo do dia solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await canal_destino.send(embed=embed)
        
        if canal != ctx.channel:
            await ctx.send(f"✅ Versículo do dia enviado para {canal.mention}")
    else:
        await ctx.send("❌ Erro ao buscar versículo do dia. Tente novamente mais tarde.")

# Comando para pesquisar por palavra-chave
@bot.command(name='pesquisar biblia')
async def pesquisar_biblia(ctx, *, termo: str, canal: discord.TextChannel = None):
    """
    Pesquisa versículos que contenham uma palavra ou frase
    Uso: *pesquisar biblia amor [#canal]
    """
    canal_destino = canal or ctx.channel
    
    # Verificar se tem permissão para enviar no canal especificado
    if canal and not canal.permissions_for(ctx.author).send_messages:
        await ctx.send("❌ Você não tem permissão para enviar mensagens nesse canal.", delete_after=10)
        return
    
    # Remover menção de canal do termo se existir
    if canal:
        termo = termo.replace(canal.mention, "").strip()
    
    await ctx.send(f"🔍 Pesquisando por '{termo}' na Bíblia...")
    
    try:
        url = f"https://www.abibliadigital.com.br/api/verses/nvi/search/{termo}"
        response = requests.get(url)
        
        if response.status_code == 200:
            dados = response.json()
            
            if dados and len(dados) > 0:
                # Limitar a 5 resultados
                resultados = dados[:5]
                
                embed = discord.Embed(
                    title=f"📚 Resultados da pesquisa: '{termo}'",
                    description=f"Encontrados {len(dados)} versículos. Mostrando os primeiros {len(resultados)}:",
                    color=0x9B59B6
                )
                
                for i, verso in enumerate(resultados, 1):
                    texto = verso['text']
                    if len(texto) > 200:
                        texto = texto[:200] + "..."
                    
                    embed.add_field(
                        name=f"{i}. {verso['book']['name']} {verso['chapter']}:{verso['number']}",
                        value=texto,
                        inline=False
                    )
                
                embed.add_field(name="Versão", value="NVI (Nova Versão Internacional)", inline=False)
                embed.set_footer(text=f"Pesquisa solicitada por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
                
                await canal_destino.send(embed=embed)
                
                if canal != ctx.channel:
                    await ctx.send(f"✅ Resultados da pesquisa enviados para {canal.mention}")
            else:
                await ctx.send(f"❌ Nenhum versículo encontrado com o termo '{termo}'.")
        else:
            await ctx.send("❌ Erro ao realizar a pesquisa. Tente novamente mais tarde.")
    
    except Exception as e:
        logger.error(f"Erro na pesquisa bíblica: {e}")
        await ctx.send("❌ Erro ao realizar a pesquisa. Tente novamente mais tarde.")

# Comando de ajuda para comandos bíblicos
@bot.command(name='ajuda biblia')
async def ajuda_biblia(ctx):
    """Mostra ajuda para comandos bíblicos"""
    embed = discord.Embed(
        title="📖 Comandos Bíblicos - Ajuda",
        description="Comandos disponíveis para consultar a Bíblia:",
        color=0x3498DB
    )
    
    embed.add_field(
        name="*versiculo [livro] [capítulo] [versículo] [#canal]",
        value="Busca um versículo específico\nExemplo: `*versiculo joão 3 16 #geral`",
        inline=False
    )
    
    embed.add_field(
        name="*versiculo diario [#canal]",
        value="Envia um versículo aleatório do dia\nExemplo: `*versiculo diario #devocional`",
        inline=False
    )
    
    embed.add_field(
        name="*pesquisar biblia [termo] [#canal]",
        value="Pesquisa versículos por palavra-chave\nExemplo: `*pesquisar biblia amor #estudo`",
        inline=False
    )
    
    embed.add_field(
        name="*ajuda biblia",
        value="Mostra esta mensagem de ajuda",
        inline=False
    )
    
    embed.add_field(
        name="📌 Observações:",
        value="• O parâmetro [#canal] é opcional\n• Se não especificar canal, enviará no canal atual\n• Use espaços normais entre as palavras\n• Versões disponíveis: NVI",
        inline=False
    )
    
    embed.set_footer(text="API: abibliadigital.com.br")
    
    await ctx.send(embed=embed)

# Tratamento de erros
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Comando em cooldown. Tente novamente em {error.retry_after:.2f} segundos.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao executar o comando.", ephemeral=True)
        logger.error(f'Erro no comando: {error}')

bot.run(TOKEN)