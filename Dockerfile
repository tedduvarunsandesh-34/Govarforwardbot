FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y git bash curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["python", "main.py"]
