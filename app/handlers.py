from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from .config import BotConfig
from .db import TaskRepository
from .keyboards import ADD_TASK, COMPLETED, MAIN_KEYBOARD, MY_TASKS


router = Router()


class TaskStates(StatesGroup):
    waiting_for_title = State()


def task_actions_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Complete a Task")],
            [KeyboardButton(text="🗑 Delete a Task")],
            [KeyboardButton(text="↩️ Main Menu")],
        ],
        resize_keyboard=True,
    )


def completed_actions_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗑 Delete a Task")],
            [KeyboardButton(text="↩️ Main Menu")],
        ],
        resize_keyboard=True,
    )


def list_text(tasks, heading: str, empty: str) -> str:
    if not tasks:
        return f"{heading}\n\n{empty}"
    return heading + "\n\n" + "\n".join(
        f"#{task.id} — {task.title}" for task in tasks
    )


async def show_menu(message: Message, config: BotConfig, state: FSMContext) -> None:
    await state.clear()
    await message.answer(config.welcome, reply_markup=MAIN_KEYBOARD)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, config: BotConfig) -> None:
    await show_menu(message, config, state)


@router.message(Command("menu"))
async def menu(message: Message, state: FSMContext, config: BotConfig) -> None:
    await show_menu(message, config, state)


@router.message(F.text == ADD_TASK)
async def add_task_start(message: Message, state: FSMContext) -> None:
    await state.set_state(TaskStates.waiting_for_title)
    await message.answer(
        "Send the task you want to add.\n\n"
        "Example: Finish my project report\n\n"
        "Send /menu to return to the main menu."
    )


@router.message(TaskStates.waiting_for_title, F.text)
async def add_task_finish(
    message: Message,
    state: FSMContext,
    repository: TaskRepository,
) -> None:
    title = " ".join((message.text or "").split()).strip()
    if not title:
        await message.answer("Please enter a task title.")
        return
    if len(title) > 500:
        await message.answer("Please keep the task title under 500 characters.")
        return

    await repository.add(message.from_user.id, title)
    await state.clear()
    await message.answer(
        f"Task added successfully.\n\n• {title}",
        reply_markup=MAIN_KEYBOARD,
    )


@router.message(F.text == MY_TASKS)
async def my_tasks(message: Message, repository: TaskRepository) -> None:
    tasks = await repository.list_active(message.from_user.id)
    if not tasks:
        await message.answer(
            list_text(tasks, "📋 Your Active Tasks", "You have no active tasks. Tap ➕ Add Task to create one."),
            reply_markup=MAIN_KEYBOARD,
        )
        return
    await message.answer(
        list_text(tasks, "📋 Your Active Tasks", ""),
        reply_markup=task_actions_keyboard(),
    )


@router.message(F.text == COMPLETED)
async def completed_tasks(message: Message, repository: TaskRepository) -> None:
    tasks = await repository.list_completed(message.from_user.id)
    if not tasks:
        await message.answer(
            list_text(tasks, "✅ Completed Tasks", "You have no completed tasks yet."),
            reply_markup=MAIN_KEYBOARD,
        )
        return
    await message.answer(
        list_text(tasks, "✅ Completed Tasks", ""),
        reply_markup=completed_actions_keyboard(),
    )


@router.message(F.text == "✅ Complete a Task")
async def prompt_complete(message: Message, repository: TaskRepository) -> None:
    tasks = await repository.list_active(message.from_user.id)
    if not tasks:
        await message.answer("There are no active tasks to complete.", reply_markup=MAIN_KEYBOARD)
        return
    await message.answer(
        "Send the number of the task to mark as completed.\n\n" +
        "\n".join(f"#{t.id} — {t.title}" for t in tasks)
    )


@router.message(F.text == "🗑 Delete a Task")
async def prompt_delete(message: Message, repository: TaskRepository) -> None:
    active = await repository.list_active(message.from_user.id)
    completed = await repository.list_completed(message.from_user.id)
    tasks = active + completed
    if not tasks:
        await message.answer("There are no tasks to delete.", reply_markup=MAIN_KEYBOARD)
        return
    await message.answer(
        "Send the number of the task to delete.\n\n" +
        "\n".join(f"#{t.id} — {t.title}" for t in tasks)
    )


@router.message(F.text == "↩️ Main Menu")
async def main_menu(message: Message, state: FSMContext, config: BotConfig) -> None:
    await show_menu(message, config, state)


@router.message(F.text.regexp(r"^\d+$"))
async def numeric_task_action(message: Message, repository: TaskRepository) -> None:
    task_id = int(message.text)
    active = await repository.list_active(message.from_user.id)
    if any(t.id == task_id for t in active):
        if await repository.complete(message.from_user.id, task_id):
            await message.answer(
                f"Task #{task_id} marked as completed.",
                reply_markup=MAIN_KEYBOARD,
            )
            return

    completed = await repository.list_completed(message.from_user.id)
    if any(t.id == task_id for t in completed):
        if await repository.delete(message.from_user.id, task_id, completed_only=True):
            await message.answer(
                f"Completed task #{task_id} deleted.",
                reply_markup=MAIN_KEYBOARD,
            )
            return

    await message.answer(
        "I couldn't find that task number. Open 📋 My Tasks or ✅ Completed and try again."
    )


@router.message()
async def fallback(message: Message, state: FSMContext, config: BotConfig) -> None:
    if await state.get_state():
        await message.answer("Please send the task title, or send /menu to return to the main menu.")
        return
    await message.answer(
        "Please use one of the three main options below, or send /start.",
        reply_markup=MAIN_KEYBOARD,
    )
