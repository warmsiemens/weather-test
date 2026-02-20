# Weather logger 

Скрипт запрашивает погоду раз в N минут, сохраняет запросы и ответы в PostgreSQL и пишет ошибки подключения/таймаутов в отдельный лог-файл.

## Быстрый старт через Docker Compose

1) Скопируйте пример окружения:
```
copy .env.example .env
```

2) Заполните `OPENWEATHER_API_KEY` в `.env`.

3) Запустите:
```
docker-compose up --build
```

## Локальный запуск (без Docker)

```
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
set DB_HOST=localhost
python main.py
```

## Переменные окружения

- `OPENWEATHER_API_KEY` — ключ OpenWeather.
- `WEATHER_INTERVAL_MINUTES` — интервал между запросами (минуты).
- `REQUEST_TIMEOUT_SECONDS` — таймаут запроса (секунды).
- `LATITUDE`/`LONGITUDE` — фиксированные координаты (если заданы, geocoder не используется).
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` — настройки PostgreSQL.
- `ERROR_LOG_FILE` — файл для ошибок подключения/таймаутов.

## SQL-запрос с JOIN (история запросов и ответы)

```
SELECT
  r.id,
  r.requested_at,
  r.latitude,
  r.longitude,
  r.status,
  r.error_type,
  r.duration_ms,
  s.city,
  s.temperature,
  s.weather_type,
  s.sunrise,
  s.sunset
FROM requests r
LEFT JOIN responses s ON s.request_id = r.id
ORDER BY r.requested_at DESC;
```
