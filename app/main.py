from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from .config import load_config
from .db import TaskRepository
from .handlers import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def configure_profile(bot: Bot, config) -> None:
    await bot.set_my_name(name=config.name)
    await bot.set_my_short_description(short_description=config.about)
    await bot.set_my_description(description=config.description)


async def main() -> None:
    config = load_config()
    repository = TaskRepository()
    await repository.init()

    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=None),
    )
    dp = Dispatcher()
    dp["config"] = config
    dp["repository"] = repository
    dp.include_router(router)

    try:
        await configure_profile(bot, config)
        me = await bot.get_me()
        logging.info("Started as @%s", me.username)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
