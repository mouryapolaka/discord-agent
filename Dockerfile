# Use an official Python runtime as a parent image
FROM python:3.11-slim

ENV BOT_TOKEN placeholder_token
ENV CHANNEL_ID placeholder_channel_id

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

# Create config.json with empty braces inside ./app/files/ directory
RUN mkdir -p ./app/files && echo "{}" > ./app/files/config.json

CMD ["python3", "agent/main.py"]