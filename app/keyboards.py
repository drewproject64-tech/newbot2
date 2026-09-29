from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

ADD_TASK = "➕ Add Task"
MY_TASKS = "📋 My Tasks"
COMPLETED = "✅ Completed"

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ADD_TASK)],
        [KeyboardButton(text=MY_TASKS)],
        [KeyboardButton(text=COMPLETED)],
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an option",
)
