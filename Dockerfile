# ใช้ Base Image ที่เป็น Ubuntu 22.04 ซึ่งเสถียร
FROM ubuntu:22.04

# ตั้งค่า noninteractive เพื่อป้องกันข้อผิดพลาดในการติดตั้ง
ENV DEBIAN_FRONTEND=noninteractive

# อัปเดต package list และติดตั้ง dependencies ที่จำเป็นทั้งหมด
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libmpv1 \
    libgstreamer-plugins-base1.0-0 \
    libgstreamer1.0-0

# สร้าง symbolic link สำหรับ python3
RUN ln -s /usr/bin/python3 /usr/bin/python

# กำหนด working directory
WORKDIR /usr/src/app

# Copy requirements.txt และติดตั้ง dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy ไฟล์โปรเจกต์ทั้งหมด
COPY . .

# กำหนด port
EXPOSE 8000

# กำหนดคำสั่งรันแอปพลิเคชัน
CMD ["flet", "run", "--host", "0.0.0.0", "app.py"]