import os
import discord
import pytesseract
import openai
import aiohttp
from PIL import Image
from discord.ext import commands

# Cấu hình Token & API Key từ biến môi trường
TOKEN = os.getenv("DISCORD_POESKILL_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ID của kênh Discord được phép sử dụng bot
ALLOWED_CHANNEL_ID = 1337325317328736308  # Cập nhật ID kênh Discord của bạn

# Khởi tạo bot với intents phù hợp
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Cấu hình OpenAI API
openai.api_key = OPENAI_API_KEY


async def download_image(url, filename):
    """Tải ảnh từ Discord về máy"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, 'wb') as f:
                    f.write(await resp.read())
                return filename
    return None


def extract_text_from_image(image_path):
    """Dùng Tesseract OCR để trích xuất văn bản từ ảnh"""
    img = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(img)
    return extracted_text


def get_skill_info_from_chatgpt(skill_name):
    """Gửi tên Skill đến ChatGPT để lấy thông tin bằng tiếng Việt"""
    prompt = f"Hãy giải thích về skill '{skill_name}' trong game Path of Exile bằng tiếng Việt."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Bạn là một chuyên gia về game Path of Exile."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response["choices"][0]["message"]["content"]


@bot.event
async def on_ready():
    print(f'✅ POESkill Bot đã kết nối với Discord! Logged in as {bot.user}')


@bot.event
async def on_message(message):
    """Nhận diện ảnh & tìm Skill"""
    if message.author == bot.user:
        return
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(("png", "jpg", "jpeg")):
                image_path = f"./temp_{attachment.filename}"
                await download_image(attachment.url, image_path)

                extracted_text = extract_text_from_image(image_path)

                # Tìm các dòng có chứa từ "Allocates" để lấy Skill
                skill_names = [line.split("Allocates")[-1].strip() for line in extracted_text.split("\n") if "Allocates" in line]

                if skill_names:
                    response_message = "**🔍 Đã nhận diện các Skill từ ảnh:**\n"
                    for skill in skill_names:
                        skill_info = get_skill_info_from_chatgpt(skill)
                        response_message += f"\n📌 **{skill}**\n{skill_info}\n"

                    await message.channel.send(response_message)
                else:
                    await message.channel.send("❌ Không tìm thấy Skill nào trong ảnh!")

    await bot.process_commands(message)


@bot.command()
async def clear(ctx, amount: int = 100):
    """Xóa toàn bộ tin nhắn trong kênh Chatbot"""
    if ctx.channel.id == ALLOWED_CHANNEL_ID:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 **Đã xóa {len(deleted)} tin nhắn trong kênh này!**", delete_after=5)


# Chạy bot
bot.run(TOKEN)
