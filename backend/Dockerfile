FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Requirements first, code second. Docker caches each step, and this step
# only re-runs when requirements.txt changes — so editing a view rebuilds in
# seconds instead of reinstalling every package.
#
# No build tools needed: psycopg2-binary ships its own libpq. Swap to plain
# psycopg2 one day and you'll need build-essential and libpq-dev here.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Static files are collected at build time, so the running container serves
# them immediately. SECRET_KEY is read at import — collectstatic does nothing
# with it, but Django refuses to start without one. DB_ENGINE is unset here,
# so settings falls back to sqlite and no database is touched.
RUN SECRET_KEY=build-only-not-a-real-secret python manage.py collectstatic --noinput

# Render sets $PORT. 8000 is only the local default.
ENV PORT=8000
EXPOSE 8000

# sh -c so $PORT expands. The flags matter:
#
#   --worker-class gthread + --threads 8
#       The default sync worker handles ONE request at a time. A chat stream
#       holds its worker open for ten to fifteen seconds, so with 2 workers
#       two conversations would block the entire site. Threads let a worker
#       hold several open connections at once, which is exactly what SSE
#       needs. Django is synchronous, so threads — not gevent — are the
#       right tool here.
#
#   --timeout 120
#       The default is 30 seconds. A long agent run would be killed
#       mid-answer.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --worker-class gthread --workers 2 --threads 8 --timeout 120 --access-logfile - --error-logfile -"]
