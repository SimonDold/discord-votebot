# Provides a Ubuntu (22.04) image with the votebot.
# Use docker-compose.yml to configure.

FROM ubuntu:22.04
MAINTAINER Simon Dold

# This will make apt install without question
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt -y upgrade && \
    apt -y install \
    git \
    python3 \
    ca-certificates \
    imagemagick \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ADD . /voteBot

# Start the votebot
CMD python3 -u /voteBot/main.py
