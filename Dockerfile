# Sử dụng Python mới nhất
FROM python:3.10

# Cập nhật hệ thống và cài đặt Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Cập nhật pip và cài đặt dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Chạy bot
CMD ["python", "bot.py"]
