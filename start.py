import os
import threading
import requests
import discord
from discord.ext import commands
from flask import Flask
import json

# ================= FLASK (CHO RENDER KHỎI TIMEOUT) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot alive"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "https://likeapisikibidi.onrender.com"

# ================= DISCORD BOT =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= MODAL =================
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

        result_text = "Không có dữ liệu"

        try:
            r = requests.get(API_URL, params=params, timeout=15)
            try:
                # 👉 JSON GỐC
                result_text = json.dumps(r.json(), indent=2, ensure_ascii=False)
            except:
                # nếu API không trả JSON
                result_text = r.text
        except Exception as e:
            result_text = str(e)

        # Discord giới hạn 4096 ký tự → cắt nếu quá dài
        if len(result_text) > 3800:
            result_text = result_text[:3800] + "\n... (cắt bớt)"

        embed = discord.Embed(
            title="❤️ FREE FIRE LIKE (RAW JSON)",
            color=0x00ff66
        )

        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )

        embed.add_field(name="👤 UID", value=uid_value, inline=False)
        embed.add_field(
            name="📦 API Response",
            value=f"```json\n{result_text}\n```",
            inline=False
        )

        embed.set_footer(text="Raw JSON từ Sikibidi Like API")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

# ================= BUTTON =================
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

# ================= SLASH COMMAND =================
@bot.tree.command(name="like", description="Gửi like Free Fire (hiện JSON gốc)")
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
        description="Bấm nút bên dưới để gửi like\n(Kết quả hiển thị JSON gốc)",
        color=0x00ff66
    )

    embed.set_author(
        name=user.display_name,
        icon_url=user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed, view=LikeView())

# ================= READY =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online: {bot.user}")

bot.run(TOKEN)