# ใช้ base image ที่เป็น Python 3.10
FROM python:3.10-slim

# ติดตั้ง system dependencies ที่จำเป็นสำหรับ Flet
# โดยเฉพาะ libmpv1 ที่เป็นสาเหตุของปัญหา
RUN apt-get update && apt-get install -y libmpv1

# กำหนด working directory ใน container
WORKDIR /usr/src/app

# Copy ไฟล์ requirements.txt และติดตั้ง Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy ไฟล์โปรเจกต์ทั้งหมด
COPY . .

# กำหนด port ที่ Flet จะใช้ในการรัน
EXPOSE 8000

# กำหนดคำสั่งเริ่มต้นสำหรับรันแอปพลิเคชัน
CMD ["flet", "run", "--host", "0.0.0.0", "app.py"]