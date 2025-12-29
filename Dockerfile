FROM python:3.8-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    git \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /Ultra-Forward-Bot

# Clone the bot
RUN git clone https://github.com/JishuDeveloper/Ultra-Forward-Bot.git .

# Copy your requirements.txt (overwrites repo one if needed)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Run the bot
CMD ["/bin/bash", "/start.sh"]
