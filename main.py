
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

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("ERRO: Token do Discord não encontrado no arquivo .env")
    print("Certifique-se de que DISCORD_TOKEN está definido no arquivo .env")
    exit(1)

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_bot')

# Configuração intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Criar bot
bot = commands.Bot(
    command_prefix='*',
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# Evento ao iniciar o bot
@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ Bot conectado com sucesso!")
    print(f"🤖 Nome: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🌐 Servidores conectados: {len(bot.guilds)}")
    print("=" * 50)
    
    # Definir status
    await bot.change_presence(
        activity=discord.Game(name="Use /ajuda ou *ajuda_biblia"),
        status=discord.Status.online
    )
    
    # Sincronizar comandos slash
    try:
        print("🔄 Sincronizando comandos slash...")
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos slash sincronizados")
        
        # Listar comandos sincronizados
        for cmd in synced:
            print(f"   📋 /{cmd.name}")
            
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")
        logger.error(f"Erro na sincronização: {e}")

# Evento quando bot entra em servidor
@bot.event
async def on_guild_join(guild):
    print(f"🆕 Bot adicionado ao servidor: {guild.name} (ID: {guild.id})")

# Boas-vindas
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="🎉 Bem-vindo(a)!",
            description=f"Olá {member.mention}! Bem-vindo(a) ao **{member.guild.name}**!",
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# ===== COMANDOS SLASH =====

@bot.tree.command(name='ajuda', description='Mostra os comandos disponíveis')
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Comandos do Bot",
        description="Lista completa de comandos disponíveis:",
        color=0x5865F2
    )
    
    embed.add_field(
        name="📋 Comandos Slash (/)",
        value="`/ajuda` - Esta mensagem\n"
              "`/ping` - Verifica latência\n"
              "`/piada` - Conta uma piada\n"
              "`/info-servidor` - Info do servidor\n"
              "`/info-usuario` - Info de usuário\n"
              "`/expulsar` - Expulsar membro\n"
              "`/banir` - Banir membro\n"
              "`/silenciar` - Silenciar membro\n"
              "`/limpar` - Limpar mensagens\n"
              "`/lembrar` - Criar lembrete",
        inline=False
    )
    
    embed.add_field(
        name="📖 Comandos Bíblicos (*)",
        value="`*versiculo` - Buscar versículo\n"
              "`*versiculo_diario` - Versículo do dia\n"
              "`*pesquisar_biblia` - Pesquisar na Bíblia\n"
              "`*ajuda_biblia` - Ajuda detalhada",
        inline=False
    )
    
    embed.set_footer(text="Use * para comandos bíblicos e / para outros comandos")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='ping', description='Verifica a latência do bot')
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=0x00ff00 if latency < 100 else 0xffff00 if latency < 200 else 0xff0000
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='piada', description='Conta uma piada de programação')
async def joke(interaction: discord.Interaction):
    jokes = [
        '🐛 Por que os programadores preferem o modo escuro? Porque a luz atrai bugs!',
        '💾 Uma consulta SQL entra em um bar e pergunta: "Posso me juntar a vocês?"',
        '👓 Por que desenvolvedores Java usam óculos? Porque não veem C#.',
        '💡 Quantos programadores para trocar uma lâmpada? Nenhum, é problema de hardware.',
        '🔢 Existem 10 tipos de pessoas: as que entendem binário e as que não.',
        '☕ Por que os programadores preferem café? Porque Java é vida!',
        '🔄 Como você chama um programador que não comenta o código? Um poeta!'
    ]
    
    embed = discord.Embed(
        title="😄 Piada de Programação",
        description=random.choice(jokes),
        color=0xffd700
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='info-servidor', description='Mostra informações do servidor')
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"ℹ️ {guild.name}",
        color=0x5865F2
    )
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="🆔 ID", value=str(guild.id), inline=True)
    embed.add_field(name="👑 Dono", value=str(guild.owner), inline=True)
    embed.add_field(name="👥 Membros", value=str(guild.member_count), inline=True)
    embed.add_field(name="📅 Criado em", value=f"<t:{int(guild.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="⭐ Nível Boost", value=str(guild.premium_tier), inline=True)
    embed.add_field(name="💎 Boosts", value=str(guild.premium_subscription_count), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='info-usuario', description='Mostra informações de um usuário')
@app_commands.describe(membro='O usuário para ver informações (opcional)')
async def userinfo(interaction: discord.Interaction, membro: discord.Member = None):
    member = membro or interaction.user
    embed = discord.Embed(
        title=f"👤 {member.display_name}",
        color=member.color if member.color != discord.Color.default() else 0x5865F2
    )
    
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=str(member.id), inline=True)
    embed.add_field(name="📅 Entrou em", value=f"<t:{int(member.joined_at.timestamp())}:D>", inline=True)
    embed.add_field(name="🎂 Conta criada", value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="🤖 Bot?", value="Sim" if member.bot else "Não", inline=True)
    embed.add_field(name="🎭 Cargos", value=str(len(member.roles) - 1), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='expulsar', description='Expulsa um usuário do servidor')
@app_commands.describe(membro='O usuário para expulsar', motivo='Motivo da expulsão')
async def kick(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Nenhum motivo fornecido"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message('❌ Você não tem permissão para expulsar membros.', ephemeral=True)
        return

    if membro == interaction.user:
        await interaction.response.send_message('❌ Você não pode se expulsar.', ephemeral=True)
        return

    if not membro.kickable:
        await interaction.response.send_message('❌ Não posso expulsar esse usuário.', ephemeral=True)
        return

    try:
        await membro.kick(reason=f"{motivo} - Por: {interaction.user}")
        embed = discord.Embed(
            title="👢 Usuário Expulso",
            description=f"**{membro}** foi expulso do servidor.",
            color=0xff9500
        )
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message('❌ Falha ao expulsar usuário.', ephemeral=True)
        logger.error(f"Erro ao expulsar: {e}")

@bot.tree.command(name='banir', description='Bane um usuário do servidor')
@app_commands.describe(membro='O usuário para banir', motivo='Motivo do banimento')
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Nenhum motivo fornecido"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message('❌ Você não tem permissão para banir membros.', ephemeral=True)
        return

    if membro == interaction.user:
        await interaction.response.send_message('❌ Você não pode se banir.', ephemeral=True)
        return

    if not membro.bannable:
        await interaction.response.send_message('❌ Não posso banir esse usuário.', ephemeral=True)
        return

    try:
        await membro.ban(reason=f"{motivo} - Por: {interaction.user}")
        embed = discord.Embed(
            title="🔨 Usuário Banido",
            description=f"**{membro}** foi banido do servidor.",
            color=0xff0000
        )
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message('❌ Falha ao banir usuário.', ephemeral=True)
        logger.error(f"Erro ao banir: {e}")

@bot.tree.command(name='silenciar', description='Silencia um usuário')
@app_commands.describe(membro='O usuário para silenciar', motivo='Motivo do silenciamento')
async def mute(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Nenhum motivo fornecido"):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message('❌ Você não tem permissão para gerenciar cargos.', ephemeral=True)
        return

    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="Muted")

    if role is None:
        try:
            role = await guild.create_role(
                name="Muted",
                color=discord.Color.dark_gray(),
                reason="Cargo criado automaticamente pelo bot"
            )
            for channel in guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False, add_reactions=False)
        except Exception as e:
            await interaction.response.send_message('❌ Falha ao criar cargo Muted.', ephemeral=True)
            logger.error(f"Erro ao criar cargo Muted: {e}")
            return

    if role in membro.roles:
        await interaction.response.send_message('❌ Este usuário já está silenciado.', ephemeral=True)
        return

    try:
        await membro.add_roles(role, reason=f"{motivo} - Por: {interaction.user}")
        embed = discord.Embed(
            title="🔇 Usuário Silenciado",
            description=f"**{membro}** foi silenciado.",
            color=0x808080
        )
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message('❌ Falha ao silenciar usuário.', ephemeral=True)
        logger.error(f"Erro ao silenciar: {e}")

@bot.tree.command(name='limpar', description='Limpa mensagens do canal')
@app_commands.describe(quantidade='Número de mensagens para apagar (1-100)')
async def clear(interaction: discord.Interaction, quantidade: int = 5):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message('❌ Você não tem permissão para gerenciar mensagens.', ephemeral=True)
        return

    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message("❌ Por favor, informe um número entre 1 e 100.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=quantidade)
    
    embed = discord.Embed(
        title="🧹 Mensagens Limpas",
        description=f"**{len(deleted)}** mensagens foram apagadas.",
        color=0x00ff00
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name='lembrar', description='Cria um lembrete')
@app_commands.describe(minutos='Tempo em minutos para o lembrete', mensagem='Mensagem do lembrete')
async def remind(interaction: discord.Interaction, minutos: int, mensagem: str):
    if minutos <= 0 or minutos > 1440:  # Máximo 24 horas
        await interaction.response.send_message('❌ O tempo deve ser entre 1 e 1440 minutos (24h).', ephemeral=True)
        return

    embed = discord.Embed(
        title="⏰ Lembrete Criado",
        description=f"Vou te lembrar em **{minutos}** minuto(s)!",
        color=0x00ff00
    )
    embed.add_field(name="Mensagem", value=mensagem, inline=False)
    await interaction.response.send_message(embed=embed)
    
    await asyncio.sleep(minutos * 60)
    
    remind_embed = discord.Embed(
        title="⏰ Lembrete!",
        description=mensagem,
        color=0xffd700
    )
    await interaction.followup.send(f"{interaction.user.mention}", embed=remind_embed)

# ===== COMANDOS BÍBLICOS COM PREFIXO =====

async def buscar_versiculo(livro, capitulo, versiculo):
    try:
        url = f"https://www.abibliadigital.com.br/api/verses/nvi/{livro}/{capitulo}/{versiculo}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar versículo: {e}")
        return None

async def buscar_versiculo_aleatorio():
    try:
        url = "https://www.abibliadigital.com.br/api/verses/nvi/random"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar versículo aleatório: {e}")
        return None

@bot.command(name='versiculo')
async def versiculo_comando(ctx, livro: str = None, capitulo: int = None, versiculo: int = None, canal: discord.TextChannel = None):
    """Busca um versículo específico da Bíblia"""
    if not livro or not capitulo or not versiculo:
        embed = discord.Embed(
            title="❌ Uso Incorreto",
            description="**Uso correto:** `*versiculo <livro> <capítulo> <versículo> [#canal]`\n**Exemplo:** `*versiculo joão 3 16`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

    canal_destino = canal or ctx.channel

    if canal and not canal.permissions_for(ctx.author).send_messages:
        await ctx.send("❌ Você não tem permissão para enviar mensagens nesse canal.")
        return

    msg = await ctx.send("🔍 Buscando versículo...")

    dados = await buscar_versiculo(livro.lower(), capitulo, versiculo)

    if dados:
        embed = discord.Embed(
            title=f"📖 {dados['book']['name']} {dados['chapter']}:{dados['number']}",
            description=f"*\"{dados['text']}\"*",
            color=0x4A90E2
        )
        embed.add_field(name="📚 Versão", value="NVI (Nova Versão Internacional)", inline=False)
        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await canal_destino.send(embed=embed)
        await msg.edit(content=f"✅ Versículo enviado{' para ' + canal.mention if canal else ''}!")
    else:
        await msg.edit(content="❌ Versículo não encontrado. Verifique se o livro, capítulo e versículo estão corretos.")

@bot.command(name='versiculo_diario')
async def versiculo_diario(ctx, canal: discord.TextChannel = None):
    """Envia um versículo aleatório do dia"""
    canal_destino = canal or ctx.channel

    if canal and not canal.permissions_for(ctx.author).send_messages:
        await ctx.send("❌ Você não tem permissão para enviar mensagens nesse canal.")
        return

    msg = await ctx.send("🙏 Buscando versículo do dia...")

    dados = await buscar_versiculo_aleatorio()

    if dados:
        embed = discord.Embed(
            title=f"🌅 Versículo do Dia",
            description=f"*\"{dados['text']}\"*",
            color=0xFFD700
        )
        embed.add_field(
            name="📍 Referência",
            value=f"{dados['book']['name']} {dados['chapter']}:{dados['number']}",
            inline=True
        )
        embed.add_field(name="📚 Versão", value="NVI", inline=True)
        embed.set_footer(
            text=f"Versículo do dia • Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await canal_destino.send(embed=embed)
        await msg.edit(content=f"✅ Versículo do dia enviado{' para ' + canal.mention if canal else ''}!")
    else:
        await msg.edit(content="❌ Erro ao buscar versículo do dia. Tente novamente mais tarde.")

@bot.command(name='pesquisar_biblia')
async def pesquisar_biblia(ctx, *, args):
    """Pesquisa versículos que contenham uma palavra ou frase"""
    parts = args.split()
    canal = None
    termo = args

    # Verificar se o último argumento é uma menção de canal
    if parts and parts[-1].startswith('<#') and parts[-1].endswith('>'):
        try:
            canal_id = int(parts[-1][2:-1])
            canal = ctx.guild.get_channel(canal_id)
            termo = ' '.join(parts[:-1])
        except ValueError:
            pass

    canal_destino = canal or ctx.channel

    if canal and not canal.permissions_for(ctx.author).send_messages:
        await ctx.send("❌ Você não tem permissão para enviar mensagens nesse canal.")
        return

    if not termo.strip():
        embed = discord.Embed(
            title="❌ Uso Incorreto",
            description="**Uso correto:** `*pesquisar_biblia <termo> [#canal]`\n**Exemplo:** `*pesquisar_biblia amor`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

    msg = await ctx.send(f"🔍 Pesquisando por **'{termo}'** na Bíblia...")

    try:
        url = f"https://www.abibliadigital.com.br/api/verses/nvi/search/{termo}"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            dados = response.json()

            if dados and len(dados) > 0:
                resultados = dados[:5]

                embed = discord.Embed(
                    title=f"📚 Resultados da Pesquisa",
                    description=f"**Termo:** {termo}\n**Resultados:** {len(dados)} encontrados (mostrando {len(resultados)})",
                    color=0x9B59B6
                )

                for i, verso in enumerate(resultados, 1):
                    texto = verso['text']
                    if len(texto) > 150:
                        texto = texto[:150] + "..."

                    embed.add_field(
                        name=f"{i}. {verso['book']['name']} {verso['chapter']}:{verso['number']}",
                        value=f"*\"{texto}\"*",
                        inline=False
                    )

                embed.add_field(name="📚 Versão", value="NVI (Nova Versão Internacional)", inline=False)
                embed.set_footer(
                    text=f"Pesquisa por {ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url
                )

                await canal_destino.send(embed=embed)
                await msg.edit(content=f"✅ Resultados enviados{' para ' + canal.mention if canal else ''}!")
            else:
                await msg.edit(content=f"❌ Nenhum versículo encontrado com o termo **'{termo}'**.")
        else:
            await msg.edit(content="❌ Erro ao realizar a pesquisa. Tente novamente mais tarde.")

    except Exception as e:
        logger.error(f"Erro na pesquisa bíblica: {e}")
        await msg.edit(content="❌ Erro ao realizar a pesquisa. Tente novamente mais tarde.")

@bot.command(name='ajuda_biblia')
async def ajuda_biblia(ctx):
    """Mostra ajuda para comandos bíblicos"""
    embed = discord.Embed(
        title="📖 Comandos Bíblicos - Ajuda",
        description="Comandos disponíveis para consultar a Bíblia Sagrada:",
        color=0x3498DB
    )

    embed.add_field(
        name="📋 Comandos Disponíveis",
        value="`*versiculo [livro] [cap] [vers] [#canal]`\n"
              "`*versiculo_diario [#canal]`\n"
              "`*pesquisar_biblia [termo] [#canal]`\n"
              "`*ajuda_biblia`",
        inline=False
    )

    embed.add_field(
        name="💡 Exemplos de Uso",
        value="`*versiculo joão 3 16`\n"
              "`*versiculo salmos 23 1 #devocional`\n"
              "`*versiculo_diario`\n"
              "`*pesquisar_biblia amor #estudo`",
        inline=False
    )

    embed.add_field(
        name="📌 Observações",
        value="• O parâmetro **[#canal]** é opcional\n"
              "• Use espaços normais entre palavras\n"
              "• Versão disponível: **NVI**\n"
              "• API: abibliadigital.com.br",
        inline=False
    )

    embed.set_footer(text="Use * (asterisco) antes dos comandos bíblicos")
    await ctx.send(embed=embed)

# ===== TRATAMENTO DE ERROS =====

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⏰ Comando em cooldown. Tente novamente em {error.retry_after:.1f} segundos.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Ocorreu um erro ao executar o comando.", ephemeral=True)
        logger.error(f'Erro no comando slash: {error}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argumento obrigatório ausente. Use `*ajuda_biblia` para ver como usar os comandos.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Argumento inválido. Use `*ajuda_biblia` para ver como usar os comandos.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando.")
    else:
        logger.error(f'Erro no comando: {error}')
        await ctx.send("❌ Ocorreu um erro ao executar o comando.")

# ===== INICIALIZAÇÃO =====

def main():
    try:
        print("🚀 Iniciando bot Discord...")
        print("⏳ Conectando...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido! Verifique o token no arquivo .env")
    except Exception as e:
        print(f"❌ ERRO ao iniciar o bot: {e}")
        logger.error(f"Erro crítico: {e}")

if __name__ == "__main__":
    main()
