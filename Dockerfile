FROM python:3.10-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    curl wget unzip build-essential \
    libssl-dev libcurl4-openssl-dev libcrypto++-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/meganz/MEGASDK/releases/download/v4.15.0/megasdkrest-linux-x64.zip \
    && unzip megasdkrest-linux-x64.zip -d /usr/local/bin \
    && rm megasdkrest-linux-x64.zip

RUN python -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6090

CMD megasdkrest --port 6090 & bash start.sh
