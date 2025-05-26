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
    embed.add_field(name='/versiculo-diario', value='Mostra o versículo do dia', inline=False)
    embed.add_field(name='/pesquisar-biblia', value='Pesquisa versículos por palavra-chave', inline=False)
    embed.add_field(name='/versiculo', value='Busca um versículo específico', inline=False)
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

# Versículo diário
@bot.tree.command(name='versiculo-diario', description='Mostra o versículo do dia')
async def daily_verse(interaction: discord.Interaction):
    try:
        # API gratuita para versículos bíblicos
        response = requests.get('https://bible-api.com/john%203:16?translation=almeida')
        
        if response.status_code == 200:
            data = response.json()
            
            embed = discord.Embed(
                title="📖 Versículo do Dia",
                description=f"*{data['text'].strip()}*",
                color=0x8B4513
            )
            embed.add_field(name="Referência", value=data['reference'], inline=False)
            embed.add_field(name="Tradução", value=data['translation_name'], inline=True)
            embed.set_footer(text="Que Deus abençoe seu dia! ✨")
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Erro ao buscar versículo. Tente novamente.", ephemeral=True)
    except Exception as e:
        logger.error(f'Erro no comando versículo diário: {e}')
        await interaction.response.send_message("Erro ao buscar versículo. Tente novamente.", ephemeral=True)

# Pesquisar na Bíblia
@bot.tree.command(name='pesquisar-biblia', description='Pesquisa versículos por palavra-chave')
@app_commands.describe(palavra='Palavra ou frase para pesquisar')
async def search_bible(interaction: discord.Interaction, palavra: str):
    try:
        # Versículos pré-definidos por temas comuns
        verses_db = {
            'amor': [
                {'ref': 'João 3:16', 'text': 'Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.'},
                {'ref': '1 Coríntios 13:4', 'text': 'O amor é sofredor, é benigno; o amor não é invejoso; o amor não trata com leviandade, não se ensoberbece.'}
            ],
            'paz': [
                {'ref': 'João 14:27', 'text': 'Deixo-vos a paz, a minha paz vos dou; não vo-la dou como o mundo a dá. Não se turbe o vosso coração, nem se atemorize.'},
                {'ref': 'Filipenses 4:7', 'text': 'E a paz de Deus, que excede todo o entendimento, guardará os vossos corações e os vossos sentimentos em Cristo Jesus.'}
            ],
            'esperança': [
                {'ref': 'Jeremias 29:11', 'text': 'Porque bem sei os pensamentos que tenho a vosso respeito, diz o Senhor; pensamentos de paz, e não de mal, para vos dar o fim que esperais.'},
                {'ref': 'Romanos 15:13', 'text': 'Ora, o Deus de esperança vos encha de todo o gozo e paz em crença, para que abundeis em esperança pela virtude do Espírito Santo.'}
            ],
            'força': [
                {'ref': 'Isaías 40:31', 'text': 'Mas os que esperam no Senhor renovarão as forças, subirão com asas como águias; correrão, e não se cansarão; caminharão, e não se fatigarão.'},
                {'ref': 'Filipenses 4:13', 'text': 'Posso todas as coisas em Cristo que me fortalece.'}
            ],
            'fé': [
                {'ref': 'Hebreus 11:1', 'text': 'Ora, a fé é o firme fundamento das coisas que se esperam, e a prova das coisas que se não veem.'},
                {'ref': 'Marcos 11:24', 'text': 'Por isso vos digo que todas as coisas que pedirdes, orando, crede receber, e tê-las-eis.'}
            ]
        }
        
        palavra_lower = palavra.lower()
        found_verses = []
        
        # Busca por palavras-chave
        for tema, verses in verses_db.items():
            if palavra_lower in tema or any(palavra_lower in verse['text'].lower() for verse in verses):
                found_verses.extend(verses)
        
        if found_verses:
            verse = random.choice(found_verses)
            embed = discord.Embed(
                title=f"📜 Resultado para: '{palavra}'",
                description=f"*{verse['text']}*",
                color=0x4169E1
            )
            embed.add_field(name="Referência", value=verse['ref'], inline=False)
            embed.set_footer(text="Continue buscando a Palavra! 🙏")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="📜 Pesquisa Bíblica",
                description=f"Não encontrei versículos relacionados a '{palavra}'.\n\nTente palavras como: amor, paz, esperança, força, fé",
                color=0xFF6347
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        logger.error(f'Erro na pesquisa bíblica: {e}')
        await interaction.response.send_message("Erro ao pesquisar. Tente novamente.", ephemeral=True)

# Buscar versículo específico
@bot.tree.command(name='versiculo', description='Busca um versículo específico')
@app_commands.describe(referencia='Referência do versículo (ex: João 3:16)')
async def get_verse(interaction: discord.Interaction, referencia: str):
    try:
        # Remove espaços e formata a referência para a API
        ref_formatted = referencia.replace(' ', '%20')
        url = f'https://bible-api.com/{ref_formatted}?translation=almeida'
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'text' in data and data['text']:
                embed = discord.Embed(
                    title="📖 Versículo Encontrado",
                    description=f"*{data['text'].strip()}*",
                    color=0x32CD32
                )
                embed.add_field(name="Referência", value=data['reference'], inline=False)
                embed.add_field(name="Tradução", value=data.get('translation_name', 'Almeida'), inline=True)
                embed.set_footer(text="Que a Palavra seja uma lâmpada para seus pés! 💡")
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"Versículo '{referencia}' não encontrado. Verifique a referência.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Versículo '{referencia}' não encontrado. Verifique a referência.", ephemeral=True)
            
    except Exception as e:
        logger.error(f'Erro ao buscar versículo: {e}')
        await interaction.response.send_message("Erro ao buscar versículo. Verifique a referência e tente novamente.", ephemeral=True)

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