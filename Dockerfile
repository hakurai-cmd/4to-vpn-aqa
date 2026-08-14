FROM python:3.12-slim

LABEL org.opencontainers.image.title="4to-vpn-aqa"
LABEL org.opencontainers.image.description="Test runner: pytest + selenium (firefox)"

# Браузер и драйвер для UI-тестов. Firefox-ESR — стабильная ветка.
# geckodriver ставим из релиза Mozilla (в Debian slim его нет отдельным пакетом),
# чтобы образ был самодостаточным и не зависел от Selenium Manager в runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    wget \
    ca-certificates \
    && wget -q -O /tmp/gd.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz \
    && tar xzf /tmp/gd.tar.gz -C /usr/local/bin \
    && rm /tmp/gd.tar.gz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала копируем только зависимости — этот слой кешируется,
# пока requirements.txt не изменился.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем — код проекта.
COPY . .

ENV HEADLESS=true \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

CMD ["pytest"]