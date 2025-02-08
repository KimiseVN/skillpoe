import os
import discord
import openai
import aiohttp
import io
from discord.ext import commands

# ✅ Lấy token từ biến môi trường
DISCORD_TOKEN = os.getenv("DISCORD_POESKILL_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("CHATGPT_API_KEY")

# 🔹 ID của kênh được phép bot hoạt động
ALLOWED_CHANNEL_ID = 1337325317328736308  # Thay bằng ID kênh Discord của bạn

# ✅ Cấu hình OpenAI API
openai.api_key = OPENAI_API_KEY

# ✅ Khởi tạo bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 📌 Khi bot kết nối thành công
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} đã sẵn sàng!")

# 📌 Gửi ảnh đến ChatGPT để phân tích
async def analyze_image_with_chatgpt(image_url):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # 🔹 Prompt yêu cầu ChatGPT phân tích ảnh như một chuyên gia POE2
    prompt = """
    Bạn là một chuyên gia về game Path of Exile 2. Tôi sẽ gửi cho bạn một hình ảnh, nhiệm vụ của bạn là phân tích nội dung của ảnh này và cung cấp thông tin chi tiết về các kỹ năng, vật phẩm hoặc nội dung liên quan đến game xuất hiện trong ảnh. 
    Hãy giải thích rõ ràng về cách sử dụng, đặc điểm và tầm quan trọng của nội dung trong ảnh.
    """

    payload = {
        "model": "gpt-4-turbo-vision",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": [{"type": "image_url", "image_url": image_url}]}
        ],
        "max_tokens": 1000
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data["choices"][0]["message"]["content"]
            else:
                return f"⚠️ Lỗi khi gửi ảnh đến ChatGPT: {response.status} - {await response.text()}"

# 📌 Xử lý khi bot nhận tin nhắn có ảnh
@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.id != ALLOWED_CHANNEL_ID:
        return

    if message.attachments:
        await message.channel.send("📷 **Đang phân tích hình ảnh... Vui lòng chờ...**")

        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ["png", "jpg", "jpeg"]):
                result = await analyze_image_with_chatgpt(attachment.url)
                await message.channel.send(f"🔎 **Kết quả phân tích:**\n{result}")

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
