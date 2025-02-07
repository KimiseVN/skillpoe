import discord
import aiohttp
import pytesseract
from PIL import Image
import io
import openai
import os

# Lấy API Key từ biến môi trường trên Railway
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ALLOWED_CHANNEL_ID = 1337325317328736308  # ID của kênh được phép sử dụng bot

if not OPENAI_API_KEY or not TOKEN:
    raise ValueError("❌ API Key hoặc Discord Token không tồn tại! Hãy thiết lập biến môi trường trên Railway.")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)
openai.api_key = OPENAI_API_KEY

async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            return io.BytesIO(await resp.read())

async def get_skill_info(skill_name):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Hãy mô tả chi tiết kỹ năng '{skill_name}' trong game Path of Exile 2."}]
    )
    return response["choices"][0]["message"]["content"]

@client.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập thành công với tên: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # Kiểm tra nếu bot hoạt động đúng kênh
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return
    
    # Kiểm tra nếu tin nhắn có hình ảnh
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg')):
                image_data = await fetch_image(attachment.url)
                if image_data:
                    image = Image.open(image_data)
                    extracted_text = pytesseract.image_to_string(image)
                    skill_name = extracted_text.strip().split('\n')[0]  # Lấy dòng đầu tiên làm tên skill
                    
                    if skill_name:
                        await message.channel.send(f"🔍 Đang tìm kiếm thông tin về kỹ năng: **{skill_name}** ...")
                        skill_info = await get_skill_info(skill_name)
                        await message.channel.send(f"📜 **Thông tin kỹ năng:**\n{skill_info}")
                    else:
                        await message.channel.send("⚠ Không nhận diện được tên kỹ năng trong ảnh. Hãy thử lại!")

client.run(TOKEN)
