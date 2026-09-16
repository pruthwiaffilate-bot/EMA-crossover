# EMA Crossover Alert

This project checks for a 9 EMA / 50 EMA crossover on 1-hour candles and sends a Telegram alert when the crossover occurs.

## How it works

- Pulls the latest 1-hour candle closes from Binance.
- Calculates the EMA 9 and EMA 50 values.
- Detects bullish or bearish crossover after each hourly candle closes.
- Sends a Telegram message if a crossover is detected.
- Runs every hour on GitHub Actions using the free cron scheduler.

## Local setup

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment file and fill in values:
   ```bash
   cp .env.example .env
   ```

4. Run the checker manually:
   ```bash
   python -m src.ema_alert
   ```

## Telegram setup

1. Create a new Telegram bot with BotFather.
2. Save the bot token as `TELEGRAM_BOT_TOKEN`.
3. Get your chat ID and save it as `TELEGRAM_CHAT_ID`.
4. Add both as GitHub repository secrets when using GitHub Actions.

## GitHub Actions

The project includes a workflow at `.github/workflows/ema-alert.yml`.
It runs every hour on the cron schedule:

```yaml
- cron: '0 * * * *'
```

This is a free, always-on schedule as long as the GitHub repository remains active.

## Notes

- The script checks the market after each 1-hour candle closes.
- You can change the symbols in `.env` or in the workflow `SYMBOLS` value.
- This is intended for market monitoring and alerting, not financial advice.
