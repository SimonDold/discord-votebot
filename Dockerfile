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

# COPY . /voteBot
# uncomment this line for local testing

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Check latest commit to decide if caching should be used
ADD "https://api.github.com/repos/SimonDold/discord-votebot/commits?per_page=1" latest_commit
# comment this line for local testing

RUN git clone https://github.com/SimonDold/discord-votebot.git voteBot/
# comment this line for local testing

# Start the votebot
CMD python3 -u /voteBot/main.py
