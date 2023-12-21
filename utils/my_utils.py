from aiogram.types import InlineQuery, CallbackQuery


def inline_index(inline_query: InlineQuery, index: int):
    args = inline_query.query.split(" ") if inline_query.query != "" else []
    return len(args) >= (index+1) and args[index]


def callback_index(callback_query: CallbackQuery, index: int):
    args = callback_query.query.split(" ") if callback_query.query != "" else []
    return len(args) >= (index+1) and args[index]
