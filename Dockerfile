FROM python:3.12-slim

LABEL org.opencontainers.image.title="4to-vpn-aqa"
LABEL org.opencontainers.image.description="Test runner: pytest + selenium (firefox)"

# Браузер и драйвер для UI-тестов. Firefox-ESR — стабильная ветка,
# firefox-geckodriver ставит WebDriver в PATH (Selenium найдёт сам).
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    firefox-geckodriver \
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