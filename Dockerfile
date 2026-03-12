FROM python:3.11.8-slim

# RUN apt-get update && apt-get install -y \
#     chromium \
#     chromium-driver \
#     wget \
#     unzip \
#     && rm -rf /var/lib/apt/lists/*

# 1. Установка Chromium и драйвера
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    # Дополнительные зависимости для headless-режима
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 2. Создаём симлинк для совместимости
RUN ln -s /usr/bin/chromium /usr/bin/google-chrome

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY ./src ./src

CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
