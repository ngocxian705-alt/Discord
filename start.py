import os
import threading
import requests
import discord
from discord.ext import commands
from flask import Flask

# ================== FLASK (MỞ PORT CHO RENDER) ==================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot alive"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ================== CONFIG ==================
TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "https://sikibidiapilike8.onrender.com/like"

# ================== DISCORD BOT ==================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================== MODAL ==================
class LikeModal(discord.ui.Modal, title="Nhập UID Free Fire"):
    uid = discord.ui.TextInput(
        label="UID",
        placeholder="VD: 1234567890",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        uid_value = self.uid.value

        params = {
            "server_name": "vn",
            "uid": uid_value
        }

        try:
            r = requests.get(API_URL, params=params, timeout=15)
            status = "✅ Thành công" if r.status_code == 200 else "❌ Thất bại"
        except:
            status = "⚠️ Lỗi API"

        embed = discord.Embed(
            title="❤️ FREE FIRE LIKE",
            color=0x00ff66
        )

        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )

        embed.add_field(name="👤 UID", value=uid_value, inline=False)
        embed.add_field(name="🌍 Server", value="VN", inline=True)
        embed.add_field(name="📡 Status", value=status, inline=True)

        embed.set_footer(text="Powered by Sikibidi Like API")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

# ================== BUTTON ==================
class LikeView(discord.ui.View):
    @discord.ui.button(label="❤️ GỬI LIKE", style=discord.ButtonStyle.success)
    async def like(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Không được dùng bot trong tin nhắn riêng!",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(LikeModal())

# ================== SLASH COMMAND ==================
@bot.tree.command(name="like", description="Gửi like Free Fire bằng nút bấm")
async def like(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ Không được dùng bot trong tin nhắn riêng!",
            ephemeral=True
        )
        return

    user = interaction.user

    embed = discord.Embed(
        title="❤️ FREE FIRE LIKE",
        description="Bấm nút bên dưới để gửi like",
        color=0x00ff66
    )

    embed.set_author(
        name=user.display_name,
        icon_url=user.display_avatar.url
    )

    await interaction.response.send_message(
        embed=embed,
        view=LikeView()
    )

# ================== READY ==================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online: {bot.user}")

bot.run(TOKEN)