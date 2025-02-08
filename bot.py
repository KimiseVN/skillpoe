import os
import discord
import openai
import aiohttp
import io
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from discord.ext import commands

# ✅ Lấy token từ biến môi trường
DISCORD_TOKEN = os.getenv("DISCORD_POESKILL_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("CHATGPT_API_KEY")

# 🔹 ID của kênh được phép bot hoạt động
ALLOWED_CHANNEL_ID = 1337325317328736308  # Thay bằng ID kênh của bạn

# 🔹 Cấu hình OpenAI API
openai.api_key = OPENAI_API_KEY

# 🔹 Cấu hình Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ✅ Khởi tạo bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 📌 Khi bot kết nối thành công
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} đã sẵn sàng!")

# 📌 Tiền xử lý ảnh trước khi chạy OCR
def preprocess_image(image):
    image = image.convert("L")  # Chuyển thành ảnh grayscale (đen trắng)
    image = ImageEnhance.Contrast(image).enhance(2)  # Tăng độ tương phản
    image = image.filter(ImageFilter.MedianFilter())  # Lọc nhiễu
    return image

# 📌 Hàm xử lý ảnh để trích xuất text
async def extract_text_from_image(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()
                image = Image.open(io.BytesIO(image_data))
                processed_image = preprocess_image(image)  # Xử lý ảnh trước khi OCR
                extracted_text = pytesseract.image_to_string(processed_image, config="--psm 7 --oem 3")  # Trích xuất text từ ảnh
                return extracted_text
            else:
                return None

# 📌 Hàm tìm tên Skill từ văn bản nhận diện
def extract_skill_name(text):
    lines = text.split("\n")
    for line in lines:
        cleaned_line = line.strip().replace("|", "").replace("-", "").replace("_", "").replace("'", "")  # Xử lý ký tự thừa
        if re.match(r"^[A-Z][a-zA-Z\s]+$", cleaned_line):  # Chỉ lấy dòng có chữ cái đầu viết hoa
            return cleaned_line
    return None

# 📌 Hàm gửi truy vấn tìm Skill đến ChatGPT
async def query_chatgpt(skill_name):
    prompt = f"Hãy cung cấp thông tin chi tiết về Skill '{skill_name}' trong game Path of Exile 2."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Lỗi khi lấy dữ liệu từ ChatGPT: {e}"

# 📌 Xử lý khi bot nhận tin nhắn có ảnh
@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.id != ALLOWED_CHANNEL_ID:
        return

    if message.attachments:
        await message.channel.send("📷 **Đang phân tích hình ảnh... Vui lòng chờ...**")
        
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ["png", "jpg", "jpeg"]):
                extracted_text = await extract_text_from_image(attachment.url)

                if extracted_text:
                    skill_name = extract_skill_name(extracted_text)
                    
                    if skill_name:
                        await message.channel.send(f"🔎 **Đang tìm thông tin Skill: {skill_name}**...")
                        result = await query_chatgpt(skill_name)
                        await message.channel.send(f"📌 **{skill_name}**\n{result}")
                    else:
                        await message.channel.send("❌ Không tìm thấy tên Skill nào trong ảnh.")
                else:
                    await message.channel.send("❌ Lỗi khi xử lý ảnh. Hãy thử lại.")

    await bot.process_commands(message)

# 📌 Lệnh !clear để xóa lịch sử tin nhắn trong kênh
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 100):
    if ctx.channel.id == ALLOWED_CHANNEL_ID:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 **Đã xóa {len(deleted)} tin nhắn trong kênh này!**", delete_after=5)
    else:
        await ctx.send("❌ Lệnh này chỉ có thể sử dụng trong kênh chỉ định.")

# Chạy bot
bot.run(DISCORD_TOKEN)
