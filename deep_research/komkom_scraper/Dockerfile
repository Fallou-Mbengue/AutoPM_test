FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir scrapy sqlalchemy python-dotenv psycopg2-binary

CMD ["scrapy", "list"]