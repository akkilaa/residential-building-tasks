# Residential building-tasks

A Telegram bot for managing recurring maintenance tasks in a residential building. Residents receive scheduled reminders directly in a group chat, confirm completion with a single button tap, and the bot automatically reschedules the next occurrence.

---

## What this solves

Running a residential building means repeating the same maintenance tasks on a schedule: 
- Adding salt tablets to the water softener
- Cleaning the garage drain
- Ordering supplies before they run out

Without a system, tasks get forgotten, done late, or duplicated.

This bot:
- Sends reminders to a Telegram group at the right time
- Re-sends the reminder on a configured interval until someone confirms
- Lets any resident mark a task done directly from the chat no app, no login
- Tracks who completed each task and when
- Monitors consumable stock (salt bags) and alerts the group when supplies are low
- Logs the full completion history to a JSON file

---

## Built around Telegram

The only interface residents need is Telegram, an app most people already have. The bot posts to a shared group chat, so everyone sees the reminders and completions without needing to install anything extra.

Tasks are confirmed with inline buttons. For multi-step tasks (like adding salt), the bot guides through a short follow-up to record how many bags were added, then automatically calculates the next due date based on that quantity.

---

## Adaptable for any building or property

The project is designed to be easy to extend. Each task type is its own class, adding a new recurring task means creating a small file following the same pattern as the existing ones. The scheduler, persistence, and notification logic require no changes.

Good candidates for additional tasks:
- Filter replacements
- Elevator inspections
- Common area cleaning
- Pest control
- Fire extinguisher checks

---

## Multiple language support

All messages sent to Telegram are stored in translation files under `translations/`. The active language is set at startup. Two locales are included out of the box:

- `sr` - Serbian (default)
- `en` - English

Switching languages or adding a new one requires no code changes - only a new JSON file in `translations/`.

---

## Getting started

**Requirements:** Python 3.9+, a Telegram bot token from [@BotFather](https://t.me/BotFather), and a Telegram group the bot has been added to.

```bash
# 1. Clone and set up a virtual environment
git clone <repo-url>
cd jelke-tasks
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install python-telegram-bot python-dotenv

# 3. Configure
cp .env.example .env
# Edit .env and fill in your BOT_TOKEN, GROUP_CHAT_ID, and ADMIN_USER_ID

# 4. Run
python main.py
```

The bot sends a startup message to the group when it connects. Use `/status` to verify everything is running.

> **CI/CD:** Deployment instructions will be added here once the pipeline is set up.

---

## Configuration

All tunables are read from `.env`. See `.env.example` for a full list with descriptions.

Key variables:

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `GROUP_CHAT_ID` | ID of the Telegram group to post in |
| `ADMIN_USER_ID` | Telegram user ID allowed to use `/remind` |
| `DAYS_PER_SALT_BAG` | Days of water softener coverage per salt bag |
| `SALT_LOW_STOCK_THRESHOLD` | Bag count that triggers a low-stock alert |
| `SCHEDULER_CHECK_INTERVAL` | Seconds between scheduler ticks (default: 3600) |
| `NOTIFICATION_RESEND_INTERVAL_HOURS` | Hours before re-sending an unacknowledged reminder |

---

## Commands

| Command | Description |
|---|---|
| `/done` | Show pending tasks as buttons to confirm completion |
| `/status` | Show all task due dates and current stock level |
| `/stanje` | Show current salt stock |
| `/remind` | Manually re-send all pending reminders (admin only) |
