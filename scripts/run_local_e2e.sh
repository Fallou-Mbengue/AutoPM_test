#!/usr/bin/env bash

set -e

# --- Check FFmpeg presence early (fail fast) ---
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: FFmpeg is not installed or not on PATH."
  echo "Please install FFmpeg before running this script."
  echo "See install instructions in README.md (brew/apt/choco/download)."
  exit 2
fi

# --- ENV VAR DEFAULTS ---
: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_USER:=postgres}"
: "${DB_PASSWORD:=postgres}"
: "${DB_NAME:=komkom}"
: "${LOCAL_STATIC_DIR:=./local_static}"

echo "Using DB_HOST=$DB_HOST"
echo "Using DB_PORT=$DB_PORT"
echo "Using DB_USER=$DB_USER"
echo "Using DB_PASSWORD=$DB_PASSWORD"
echo "Using DB_NAME=$DB_NAME"
echo "Using LOCAL_STATIC_DIR=$LOCAL_STATIC_DIR"

# Ensure repo root is in Python path so Scrapy + pipelines can import deep_research.*
export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"

# --- STATIC DIR ---
if [ ! -d "$LOCAL_STATIC_DIR" ]; then
  echo "Creating LOCAL_STATIC_DIR at $LOCAL_STATIC_DIR"
  mkdir -p "$LOCAL_STATIC_DIR"
fi

# --- CREATE TABLES ---
echo "Creating tables..."
python deep_research/create_tables.py

# --- BUILD AND RUN SCRAPER DOCKER ---
echo "Building komkom_scraper Docker image..."
docker build -t komkom_scraper_test deep_research/komkom_scraper

echo "Running komkom_scraper container..."
docker run --rm \
  -e DB_HOST="$DB_HOST" \
  -e DB_PORT="$DB_PORT" \
  -e DB_USER="$DB_USER" \
  -e DB_PASSWORD="$DB_PASSWORD" \
  -e DB_NAME="$DB_NAME" \
  komkom_scraper_test scrapy crawl adepme_spider

# --- BUILD EPISODE ---
echo "Building episode for user 1 (lang=fr)..."
EPISODE_OUT=$(python scripts/run_episode_builder.py)
SUCCESS=$?

if [ $SUCCESS -ne 0 ]; then
  echo "Episode build failed!"
  exit 1
fi

MP3_PATH=$(echo "$EPISODE_OUT" | python -c "import sys, json; print(json.load(sys.stdin)['mp3_url'])")
echo "SUCCESS: Episode built. MP3: $MP3_PATH"