# Sử dụng image có sẵn Python
FROM python:3.12

# Cài đặt Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy toàn bộ file trong repo vào container
COPY . .

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Chạy bot
CMD ["python", "bot.py"]
