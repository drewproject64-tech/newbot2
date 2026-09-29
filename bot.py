"""Compatibility entrypoint for Render services configured with: python bot.py."""

import asyncio

from app.main import main


if __name__ == "__main__":
    asyncio.run(main())
