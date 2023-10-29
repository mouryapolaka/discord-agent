# Use an official Python runtime as a parent image
FROM python:3.11-slim

ENV DISCORD_BOT_TOKEN placeholder_token

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python3", "agent/main.py"]