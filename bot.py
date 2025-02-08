import os
import discord
import openai
from discord.ext import commands

# Lấy Token từ biến môi trường
DISCORD_TOKEN = os.getenv("DISCORD_POESKILL_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("CHATGPT_API_KEY")

# ID của kênh được phép bot hoạt động
ALLOWED_CHANNEL_ID = 1337325317328736308

# Cấu hình bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Khởi tạo OpenAI client
openai.api_key = OPENAI_API_KEY

async def process_image(image_url):
    """Gửi ảnh lên OpenAI GPT-4 Turbo để phân tích"""
    try:
        print(f"📤 Đang gửi ảnh đến OpenAI: {image_url}")  # Debug log
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Bạn là một chuyên gia về game Path of Exile 2, hãy phân tích nội dung trong ảnh và cung cấp thông tin liên quan."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Phân tích thông tin trong ảnh này và cung cấp thông tin liên quan đến Path of Exile 2."},
                    {"type": "image_url", "image_url": {"url": image_url}}  # Fix: image_url phải là object
                ]}
            ]
        )
        result = response["choices"][0]["message"]["content"]
        print(f"✅ Kết quả từ OpenAI:\n{result}")  # Debug log
        return result
    except openai.error.OpenAIError as e:
        print(f"⚠️ Lỗi OpenAI: {e}")  # Debug log
        return f"⚠️ Lỗi khi gửi ảnh đến ChatGPT: {e}"

@bot.event
async def on_ready():
    """Thông báo khi bot sẵn sàng"""
    print(f"✅ Bot đã kết nối với Discord! Logged in as {bot.user}")

@bot.event
async def on_message(message):
    """Xử lý khi có người gửi ảnh"""
    if message.author == bot.user or message.channel.id != ALLOWED_CHANNEL_ID:
        return

    print(f"📨 Nhận tin nhắn từ {message.author}: {message.content}")  # Debug log

    if message.attachments:
        for attachment in message.attachments:
            if attachment.url.endswith(("png", "jpg", "jpeg")):  # Chỉ nhận ảnh
                await message.channel.send("📤 **Đang phân tích hình ảnh... Vui lòng chờ...**")
                result = await process_image(attachment.url)
                await message.channel.send(f"🔎 **Kết quả phân tích:**\n{result}")
                return

    await bot.process_commands(message)  # Xử lý các lệnh khác nếu có

# Khởi chạy bot
bot.run(DISCORD_TOKEN)
