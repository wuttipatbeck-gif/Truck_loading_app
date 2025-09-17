FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y libmpv1

# Set up working directory
WORKDIR /usr/src/app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose the port Flet will run on
EXPOSE 8000

# Define the start command
CMD ["flet", "run", "--host", "0.0.0.0", "app.py"]