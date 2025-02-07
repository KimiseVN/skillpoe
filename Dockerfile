# Sử dụng Python mới nhất
FROM python:3.10

# Cập nhật hệ thống và cài đặt Tesseract OCR (cho pytesseract)
RUN apt-get update && apt-get install -y tesseract-ocr

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép tất cả mã nguồn vào container
COPY . .

# Cài đặt dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Chạy bot
CMD ["python", "bot.py"]
