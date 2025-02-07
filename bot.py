import os
import discord
import openai
import requests
from io import BytesIO
from discord.ext import commands

# Lấy Token từ biến môi trường
TOKEN = os.getenv("DISCORD_POESKILL_BOT_TOKEN")  
OPENAI_API_KEY = os.getenv("CHATGPT_API_KEY")

# ID của kênh được phép bot hoạt động
ALLOWED_CHANNEL_ID = 1337325317328736308  

# Thiết lập intents cho bot
intents = discord.Intents.default()
intents.message_content = True

# Khởi tạo bot với prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Cấu hình OpenAI API
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@bot.event
async def on_ready():
    print(f'✅ POESkill Bot đã kết nối với Discord! Logged in as {bot.user}')

@bot.event
async def on_message(message):
    """Xử lý tin nhắn từ người dùng"""
    if message.author == bot.user:
        return
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return  # Chỉ phản hồi trong kênh chỉ định

    # Nếu có ảnh đính kèm, xử lý ảnh
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(("png", "jpg", "jpeg")):
                await process_image(message, attachment)
    
    await bot.process_commands(message)

async def process_image(message, attachment):
    """Tải ảnh và gửi lên ChatGPT API để phân tích"""
    try:
        await message.channel.send("📤 Đang phân tích hình ảnh... Vui lòng chờ...")

        # Tải ảnh về
        img_data = requests.get(attachment.url).content
        img_file = BytesIO(img_data)

        # Gửi ảnh lên OpenAI API
        response = client.chat.completions.create(
        model="chatgpt-4o-latest",  # 🔹 Cập nhật mô hình mới nhất
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia về Path of Exile 2."},
            {"role": "user", "content": [
                {"type": "text", "text": "Hãy phân tích nội dung trong hình ảnh này và cho biết nó liên quan đến kỹ năng, vật phẩm, hoặc cơ chế nào trong Path of Exile 2."},
                {"type": "image_url", "image_url": {"url": attachment.url}}
            ]}
            ],
        max_tokens=500
        )

        # Trích xuất câu trả lời
        answer = response.choices[0].message.content
        await message.channel.send(f"🔎 **Phân tích hình ảnh:**\n{answer}")

    except Exception as e:
        await message.channel.send(f"❌ Lỗi khi xử lý ảnh: {str(e)}")

bot.run(TOKEN)
