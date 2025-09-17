# ใช้ Base Image ที่เป็น Ubuntu 22.04 ซึ่งเสถียร
FROM ubuntu:22.04

# ตั้งค่า ENV เพื่อป้องกันข้อผิดพลาดในขณะติดตั้ง
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# อัปเดต package list และติดตั้ง System Dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libmpv1 \
    libgstreamer-plugins-base1.0-0 \
    libgstreamer1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# สร้าง symbolic link สำหรับ python3
RUN ln -s /usr/bin/python3 /usr/bin/python

# กำหนด working directory
WORKDIR /usr/src/app

# Copy requirements.txt และติดตั้ง Python Dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy ไฟล์โปรเจกต์ทั้งหมด
COPY . .

# กำหนด Port
EXPOSE 8000

# กำหนดคำสั่งรันแอปพลิเคชัน
CMD ["flet", "run", "--host", "0.0.0.0", "app.py"]