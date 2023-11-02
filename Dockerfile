# Use an official Python runtime as a parent image
FROM --platform=$BUILDPLATFORM python:3.11-slim

ENV BOT_TOKEN placeholder_token
ENV CHANNEL_ID placeholder_channel_id

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python3", "agent/main.py"]