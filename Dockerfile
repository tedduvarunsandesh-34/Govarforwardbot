FROM python:3.10-slim-bullseye

# 1. Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (Important for Speed Logs)
ENV PYTHONUNBUFFERED 1

# 2. Install System Dependencies
# 'gcc' and 'python3-dev' are CRITICAL for compiling TgCrypto (Speed Boost)
# 'ffmpeg' is needed for thumbnails and video attributes
RUN apt-get update && apt-get install -y \
    git \
    bash \
    curl \
    ffmpeg \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# 3. Install Python Requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# 4. Start the Bot
CMD ["python", "main.py"]

