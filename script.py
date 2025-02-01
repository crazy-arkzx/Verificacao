# SISTEMA DE VERIFICACAO PARA SEU SERVIDOR
# FEITO POR: Crazy_ArKzX
# GitHub: https://github.com/crazy-arkzx

import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random
import string

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT
                )''')
conn.commit()

ROLE_ID = 12345678910  # ID do cargo que o membro ira receber apos ser verificado
CHANNEL_ID = 12345678910  # ID do canal onde o comando deve ser usado
LOG_CHANNEL_ID = 12345678910  # ID do Canal de Logs

@bot.event
async def on_ready():
    print(f"Sistema de Verificacao | Carregado com Sucesso")
    try:
        synced = await bot.tree.sync()
        print(f"Comandos Sincronizados ({len(synced)})")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

def criar_embed(descricao, cor=discord.Color.blue()):
    return discord.Embed(description=descricao, color=cor)

def gerar_codigos():
    codigo_correto = ''.join(random.choices(string.ascii_uppercase, k=5))
    codigos_errados = [''.join(random.choices(string.ascii_uppercase, k=5)) for _ in range(4)]
    codigos = codigos_errados + [codigo_correto]
    random.shuffle(codigos)
    return codigos, codigo_correto

class CodigoMenu(discord.ui.View):
    def __init__(self, user_id, codigos, codigo_correto, interaction):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.codigo_correto = codigo_correto
        self.interaction = interaction

        self.select = discord.ui.Select(
            placeholder="Selecione o codigo correto",
            options=[discord.SelectOption(label=code, value=code) for code in codigos]
        )
        self.select.callback = self.selecionar_codigo
        self.add_item(self.select)

    async def selecionar_codigo(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(embed=criar_embed("Essa Verificacao nao e Sua!", discord.Color.red()), ephemeral=True)
            return

        escolha = self.select.values[0]
        if escolha == self.codigo_correto:
            role = interaction.guild.get_role(ROLE_ID)
            if role:
                await interaction.user.add_roles(role)
                await interaction.response.edit_message(embed=criar_embed(f"{interaction.user.mention}, Verificado com Sucesso!", discord.Color.green()), view=None)

                log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    embed_log = discord.Embed(
                        title="VERIFICACAO",
                        description=f"{interaction.user.mention} Acabou de se Verificar!",
                        color=discord.Color.green()
                    )
                    embed_log.set_footer(text=" ArKzX Team ")
                    await log_channel.send(embed=embed_log)
            else:
                await interaction.response.edit_message(embed=criar_embed("Error", discord.Color.red()), view=None)
        else:
            await interaction.response.edit_message(embed=criar_embed("Codigo Incorreto!", discord.Color.red()), view=None)

@bot.tree.command(name="verificar", description="Para Verificar-se no Servidor")
async def registrar(interaction: discord.Interaction):
    if interaction.channel.id != CHANNEL_ID:
        await interaction.response.send_message(embed=criar_embed("Este Comando so Pode ser Usado no Canal de Verificacao!", discord.Color.red()), ephemeral=True)
        return

    user_id = interaction.user.id

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        await interaction.response.send_message(embed=criar_embed("Voce ja Esta Registrado!", discord.Color.red()), ephemeral=True)
    else:
        codigos, codigo_correto = gerar_codigos()
        embed = criar_embed(f" **Selecione o Codigo Correto:**\n\n`{codigo_correto}`", discord.Color.blue())
        view = CodigoMenu(interaction.user.id, codigos, codigo_correto, interaction)
        await interaction.response.send_message(embed=embed, view=view)

bot.run("SEU_TOKEN")