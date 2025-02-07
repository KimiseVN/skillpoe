# Sử dụng Python mới nhất
FROM python:3.10

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ code vào container
COPY . .

# Cập nhật pip và cài đặt các dependencies
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Chạy bot
CMD ["bash", "-c", "source venv/bin/activate && python bot.py"]
