import os
import discord
import requests
import pytesseract
from PIL import Image
from io import BytesIO
from discord.ext import commands

# Lấy Token từ biến môi trường
DISCORD_TOKEN = os.getenv("DISCORD_POESKILL_BOT_TOKEN")  # Token bot Discord
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")  # API Key của ChatGPT

# ID của kênh được phép bot hoạt động
ALLOWED_CHANNEL_ID = 1337203470167576607  # Cập nhật Channel ID của bạn

# Thiết lập intents cho bot
intents = discord.Intents.default()
intents.message_content = True

# Khởi tạo bot với prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ POESkill Bot đã kết nối với Discord! Logged in as {bot.user}')

@bot.event
async def on_message(message):
    """Xử lý tin nhắn và nhận diện Skill từ ảnh"""
    if message.author == bot.user or message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # Xử lý ảnh nếu có ảnh đính kèm
    if message.attachments:
        await process_image(message, message.attachments[0])

    await bot.process_commands(message)

async def process_image(message, attachment):
    """Trích xuất thông tin Skill từ ảnh và gửi truy vấn đến ChatGPT"""
    try:
        img_url = attachment.url
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))

        # Sử dụng Tesseract OCR để trích xuất văn bản
        extracted_text = pytesseract.image_to_string(img)
        print(f"🔍 OCR Extracted Text: {extracted_text}")  # Debugging

        if extracted_text.strip():
            # Gửi truy vấn đến ChatGPT để lấy thông tin bằng tiếng Việt
            translated_info = get_skill_info_from_chatgpt(extracted_text)
            await message.channel.send(f"📝 **Thông tin về Skill (Tiếng Việt):**\n{translated_info}")
        else:
            await message.channel.send("⚠️ Không thể trích xuất thông tin từ ảnh. Hãy thử ảnh khác!")

    except Exception as e:
        await message.channel.send(f"❌ Lỗi xử lý ảnh: {str(e)}")

def get_skill_info_from_chatgpt(skill_text):
    """Gửi truy vấn đến ChatGPT API và lấy câu trả lời bằng tiếng Việt"""
    try:
        headers = {
            "Authorization": f"Bearer {CHATGPT_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": f"Dịch và giải thích kỹ năng này từ Path of Exile sang tiếng Việt: {skill_text}"}],
            "temperature": 0.7,
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Lỗi khi truy vấn ChatGPT API: {response.text}"

    except Exception as e:
        return f"❌ Lỗi xử lý API: {str(e)}"

bot.run(DISCORD_TOKEN)
