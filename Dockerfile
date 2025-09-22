# ใช้ Base Image ที่เป็น Ubuntu 22.04 (Jammy Jellyfish) ซึ่งเสถียร
FROM ubuntu:22.04

# ตั้งค่า ENV เพื่อป้องกันข้อผิดพลาดในขณะติดตั้งและทำให้ Python ไม่มีการบัฟเฟอร์
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# อัปเดต package list และติดตั้ง System Dependencies ที่จำเป็น
# นี่คือการแก้ปัญหาหลัก: libmpv1 และ gstreamer
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libmpv1 \
    libgstreamer-plugins-base1.0-0 \
    libgstreamer1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# สร้าง symbolic link สำหรับ python3
RUN ln -s /usr/bin/python3 /usr/bin/python

# กำหนด working directory ภายใน container
WORKDIR /usr/src/app

# Copy requirements.txt และติดตั้ง Python Dependencies
COPY requirements.txt ./
# ใช้ pip3 เพราะเราติดตั้ง python3-pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy ไฟล์โปรเจกต์ทั้งหมด
COPY . .

# กำหนด Port ที่ Flet App จะรัน (8000 เป็นค่ามาตรฐานของ Flet)
EXPOSE 8000

# กำหนดคำสั่งรันแอปพลิเคชัน
# ใช้ flet run --host 0.0.0.0 app.py เพื่อให้เปิดรับการเชื่อมต่อภายนอก (ตรงกับที่ตั้งค่าบน Koyeb)
CMD ["flet", "run", "--host", "0.0.0.0", "app.py"]