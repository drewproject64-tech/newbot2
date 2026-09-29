# SB24 Luky — Telegram Task Bot

A simple Telegram task/to-do list bot for creating, reviewing, completing, and removing personal tasks.

## Core interface
The main menu has exactly three primary buttons:
- ➕ Add Task
- 📋 My Tasks
- ✅ Completed

All bot functionality stays inside Telegram. No external links or redirects are used.

## Requirements
- Python 3.12+
- Telegram bot token

## Environment
Set BOT_TOKEN to the token issued by @BotFather.

## Local run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="YOUR_TOKEN"
python -m app.main
```

## Render
This repository includes render.yaml for a Python background worker. Set BOT_TOKEN as a secret environment variable.

## Data
SQLite stores task data per Telegram user. The database is created automatically at runtime.

## Ads-oriented design
The bot's stated purpose, profile text, welcome message, buttons, and functionality all describe the same task-management use case. There are no gambling, casino, betting, prize, payment, external-link, or redirect features.

Telegram Ads approval is not guaranteed; final moderation decisions are made by Telegram.
