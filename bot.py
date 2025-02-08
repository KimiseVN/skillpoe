import os
import discord
import requests
from discord.ext import commands
import openai
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Lấy các biến môi trường
TOKEN = os.getenv("DISCORD_POESKILL_BOT_TOKEN")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID"))

# Cấu hình OpenAI API
openai.api_key = CHATGPT_API_KEY
openai.organization = OPENAI_ORGANIZATION

# Khởi tạo bot Discord với intents phù hợp
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Khi bot kết nối
@bot.event
async def on_ready():
    print(f"✅ Bot đã kết nối: {bot.user}")

# Xử lý tin nhắn trong kênh chỉ định
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # Nếu tin nhắn có đính kèm ảnh
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(("png", "jpg", "jpeg")):
                await message.channel.send("📤 **Đang phân tích hình ảnh... Vui lòng chờ...**")
                image_url = attachment.url
                response_text = await analyze_image(image_url)
                await message.channel.send(response_text)
    
    # Xử lý lệnh bot
    await bot.process_commands(message)

# Hàm gửi ảnh lên OpenAI để phân tích
async def analyze_image(image_url):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Sử dụng model có hỗ trợ hình ảnh
            messages=[
                {"role": "system", "content": "Bạn là trợ lý chuyên tìm kiếm thông tin về game Path of Exile 2."},
                {"role": "user", "content": f"Hãy phân tích và cho tôi biết thông tin của hình ảnh này trong game POE2: {image_url}"}
            ]
        )
        return f"📝 **Kết quả phân tích:**\n{response['choices'][0]['message']['content']}"
    except Exception as e:
        return f"❌ **Lỗi khi xử lý ảnh:** {str(e)}"

# Lệnh !clear để xóa lịch sử chat trong kênh
@bot.command()
async def clear(ctx, amount: int = 100):
    """Xóa tin nhắn trong kênh Chatbot"""
    if ctx.channel.id == ALLOWED_CHANNEL_ID:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 **Đã xóa {len(deleted)} tin nhắn!**", delete_after=5)

# Chạy bot
bot.run(TOKEN)
