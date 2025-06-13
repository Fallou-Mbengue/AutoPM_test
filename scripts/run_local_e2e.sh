#!/usr/bin/env bash

set -e

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

# --- STATIC DIR ---
if [ ! -d "$LOCAL_STATIC_DIR" ]; then
  echo "Creating LOCAL_STATIC_DIR at $LOCAL_STATIC_DIR"
  mkdir -p "$LOCAL_STATIC_DIR"
fi

# --- CREATE TABLES ---
echo "Creating tables..."
python deep_research/create_tables.py

# --- RUN SPIDER (skip if scrapy not installed) ---
if command -v scrapy &> /dev/null; then
  echo "Running scrapy spider (adepme_opportunity)..."
  (cd deep_research/komkom_scraper && scrapy crawl adepme_opportunity)
else
  echo "scrapy not installed, skipping spider run."
fi

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