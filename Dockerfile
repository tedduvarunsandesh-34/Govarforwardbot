FROM python:3.8-slim-bullseye

# Avoid interactive apt
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /Ultra-Forward-Bot

# Copy requirements first (better cache)
COPY requirements.txt .

# Upgrade pip & install python deps
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Clone your bot repo
RUN git clone https://github.com/JishuDeveloper/Ultra-Forward-Bot.git .

# Copy start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Start the bot
CMD ["/bin/bash", "/start.sh"]
