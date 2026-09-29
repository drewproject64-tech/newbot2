from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BotConfig:
    token: str
    name: str = "SB24 Luky"
    username: str = "@SB24TaskBot"
    about: str = "Simple task and to-do list manager."
    description: str = (
        "SB24 Luky helps you manage a personal to-do list in Telegram. "
        "Add tasks, review active tasks, mark them complete, and keep completed tasks organized."
    )
    welcome: str = (
        "Welcome to SB24 Luky!\n\n"
        "Manage your personal to-do list directly in Telegram.\n\n"
        "Use the three buttons below to add a task, view your active tasks, or review completed tasks."
    )


def load_config() -> BotConfig:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is required.")
    return BotConfig(token=token)
