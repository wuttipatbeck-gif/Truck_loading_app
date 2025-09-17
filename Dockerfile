# ใช้ base image ที่เป็น Python 3.10
FROM python:3.10-slim

# อัปเดต package list และติดตั้ง dependencies ที่จำเป็นทั้งหมด
RUN apt-get update && apt-get install -y \
    libmpv1 \
    libgstreamer-plugins-base1.0-0 \
    libgstreamer1.0-0

# กำหนด working directory
WORKDIR /usr/src/app

# Copy requirements.txt และติดตั้ง dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy ไฟล์โปรเจกต์ทั้งหมด
COPY . .

# กำหนด port
EXPOSE 8000

# กำหนดคำสั่งรันแอปพลิเคชัน
CMD ["flet", "run", "--host", "0.0.0.0", "app.py"]