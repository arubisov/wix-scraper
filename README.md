# Wix Scraper

WIP. We started with https://github.com/ryanhlewis/WixScraper and it was a bust.

basic operation:

Create local .env file with keys required by config.py model.

```
uv run --env-file .env python scrape.py
uv run --env-file .env python compare.py <results/old_dir> <results/new_dir>
uv run --env-file .env python send_email.py <results/exports/new_dir>
```
