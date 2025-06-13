# Komkom News: Deep Research Scraper

Phase 1 scaffold for robust, extensible opportunity data scraping, normalization, and storage.

## Directory Structure

```
deep_research/
    komkom_scraper/
        items.py
        pipelines.py
        settings.py
        spiders/
            sample_opportunity.py
    db/
        database.py
        models.py
    create_tables.py
tests/
    test_normalization.py
    test_db_insert.py
requirements.txt
```

## Setup

1. **Clone repo and install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables** (for Postgres connection):
   - `DB_HOST`
   - `DB_PORT`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`

   You may use a `.env` file in `deep_research/`:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=youruser
   DB_PASSWORD=yourpass
   DB_NAME=komkom_db
   ```

3. **Initialize Database Schema:**
   ```sh
   python deep_research/create_tables.py
   ```

4. **Run Scraper Example:**
   ```sh
   cd deep_research/komkom_scraper
   scrapy crawl sample_opportunity
   ```

5. **Running Tests:**
   ```sh
   pytest
   ```

## Scheduling

For now, use `cron` or any scheduler to run, e.g.:
```
0 * * * * cd /path/to/komkom_news/deep_research/komkom_scraper && scrapy crawl sample_opportunity
```